import json

import pytest

from src.vector_store_utils import (
    clear_vector_store,
    delete_chunks_by_source,
    get_vector_store_stats,
    list_chunk_metadata,
    main,
)


class FakeCollection:
    def __init__(
        self,
        *,
        name: str = "agentic_rag_docs",
        count_value: int = 0,
        metadatas: list[dict | None] | None = None,
        ids: list[str] | None = None,
        source_to_ids: dict[str, list[str]] | None = None,
    ) -> None:
        self.name = name
        self.count_value = count_value
        self.metadatas = metadatas or []
        self.ids = ids or []
        self.source_to_ids = source_to_ids or {}
        self.get_calls: list[dict] = []
        self.delete_calls: list[list[str]] = []

    def count(self) -> int:
        return self.count_value

    def get(
        self,
        include: list[str] | None = None,
        limit: int | None = None,
        where: dict | None = None,
    ) -> dict:
        self.get_calls.append(
            {
                "include": include,
                "limit": limit,
                "where": where,
            }
        )

        if where and "source" in where:
            return {"ids": self.source_to_ids.get(where["source"], [])}

        ids = self.ids[:limit] if limit is not None else self.ids
        metadatas = self.metadatas[:limit] if limit is not None else self.metadatas
        return {"ids": ids, "metadatas": metadatas}

    def delete(self, ids: list[str]) -> None:
        self.delete_calls.append(ids)


def test_get_vector_store_stats_reports_chunk_count_and_sources(monkeypatch) -> None:
    """Stats should include the collection name, total chunks, and unique sources."""
    fake_collection = FakeCollection(
        count_value=3,
        metadatas=[
            {"source": "alpha.md"},
            {"source": "beta.md"},
            {"source": "alpha.md"},
        ],
    )
    monkeypatch.setattr(
        "src.vector_store_utils._get_collection",
        lambda: fake_collection,
    )

    stats = get_vector_store_stats()

    assert stats == {
        "collection_name": "agentic_rag_docs",
        "total_chunks": 3,
        "sources": ["alpha.md", "beta.md"],
    }
    assert fake_collection.get_calls == [
        {"include": ["metadatas"], "limit": None, "where": None}
    ]


def test_list_chunk_metadata_returns_trimmed_rows(monkeypatch) -> None:
    """Chunk metadata listing should return only the requested inspection fields."""
    fake_collection = FakeCollection(
        ids=[
            "alpha::page-1::chunk-0",
            "alpha::page-1::chunk-1",
        ],
        metadatas=[
            {"source": "alpha.md", "page": 1, "chunk_index": 0, "extra": "ignore"},
            {"source": "alpha.md", "page": 1, "chunk_index": 1},
        ],
    )
    monkeypatch.setattr(
        "src.vector_store_utils._get_collection",
        lambda: fake_collection,
    )

    rows = list_chunk_metadata(limit=1)

    assert rows == [
        {
            "chunk_id": "alpha::page-1::chunk-0",
            "source": "alpha.md",
            "page": 1,
            "chunk_index": 0,
        }
    ]
    assert fake_collection.get_calls == [
        {"include": ["metadatas"], "limit": 1, "where": None}
    ]


def test_delete_chunks_by_source_removes_matching_ids(monkeypatch) -> None:
    """Deleting by source should remove only the chunks that belong to that file."""
    fake_collection = FakeCollection(
        source_to_ids={
            "alpha.md": ["alpha::0", "alpha::1"],
            "beta.md": ["beta::0"],
        }
    )
    monkeypatch.setattr(
        "src.vector_store_utils._get_collection",
        lambda: fake_collection,
    )

    deleted_count = delete_chunks_by_source("alpha.md")

    assert deleted_count == 2
    assert fake_collection.get_calls == [
        {"include": [], "limit": None, "where": {"source": "alpha.md"}}
    ]
    assert fake_collection.delete_calls == [["alpha::0", "alpha::1"]]


def test_delete_chunks_by_source_skips_delete_when_no_matches(monkeypatch) -> None:
    """Deleting an unknown source should not call the collection delete API."""
    fake_collection = FakeCollection(source_to_ids={})
    monkeypatch.setattr(
        "src.vector_store_utils._get_collection",
        lambda: fake_collection,
    )

    deleted_count = delete_chunks_by_source("missing.md")

    assert deleted_count == 0
    assert fake_collection.delete_calls == []


def test_clear_vector_store_deletes_all_ids(monkeypatch) -> None:
    """Clearing the vector store should delete every stored chunk ID."""
    fake_collection = FakeCollection(
        count_value=3,
        ids=["chunk-0", "chunk-1", "chunk-2"],
    )
    monkeypatch.setattr(
        "src.vector_store_utils._get_collection",
        lambda: fake_collection,
    )

    deleted_count = clear_vector_store()

    assert deleted_count == 3
    assert fake_collection.get_calls == [
        {"include": [], "limit": None, "where": None}
    ]
    assert fake_collection.delete_calls == [["chunk-0", "chunk-1", "chunk-2"]]


def test_clear_vector_store_skips_delete_when_empty(monkeypatch) -> None:
    """An empty collection should return zero without calling delete."""
    fake_collection = FakeCollection(count_value=0)
    monkeypatch.setattr(
        "src.vector_store_utils._get_collection",
        lambda: fake_collection,
    )

    deleted_count = clear_vector_store()

    assert deleted_count == 0
    assert fake_collection.get_calls == []
    assert fake_collection.delete_calls == []


def test_cli_stats_prints_json(monkeypatch, capsys) -> None:
    """The stats command should print JSON output for scripting."""
    monkeypatch.setattr(
        "src.vector_store_utils.get_vector_store_stats",
        lambda: {"collection_name": "agentic_rag_docs", "total_chunks": 2, "sources": ["alpha.md"]},
    )

    exit_code = main(["stats"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {
        "collection_name": "agentic_rag_docs",
        "total_chunks": 2,
        "sources": ["alpha.md"],
    }


def test_cli_list_metadata_prints_json(monkeypatch, capsys) -> None:
    """The metadata command should honor the passed limit and print JSON."""
    observed: dict[str, int] = {}

    def fake_list_chunk_metadata(limit: int = 50) -> list[dict]:
        observed["limit"] = limit
        return [{"chunk_id": "alpha::0", "source": "alpha.md", "page": 1, "chunk_index": 0}]

    monkeypatch.setattr(
        "src.vector_store_utils.list_chunk_metadata",
        fake_list_chunk_metadata,
    )

    exit_code = main(["list-metadata", "--limit", "1"])

    assert exit_code == 0
    assert observed == {"limit": 1}
    assert json.loads(capsys.readouterr().out) == [
        {
            "chunk_id": "alpha::0",
            "source": "alpha.md",
            "page": 1,
            "chunk_index": 0,
        }
    ]


def test_cli_delete_source_requires_yes() -> None:
    """Destructive delete operations should require an explicit confirmation flag."""
    with pytest.raises(SystemExit) as error:
        main(["delete-source", "alpha.md"])

    assert error.value.code == 2


def test_cli_delete_source_prints_deleted_count(monkeypatch, capsys) -> None:
    """The delete-source command should report how many chunks were removed."""
    monkeypatch.setattr(
        "src.vector_store_utils.delete_chunks_by_source",
        lambda source: 2 if source == "alpha.md" else 0,
    )

    exit_code = main(["delete-source", "alpha.md", "--yes"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {
        "source": "alpha.md",
        "deleted_chunks": 2,
    }


def test_cli_clear_requires_yes() -> None:
    """Clearing the full store should require an explicit confirmation flag."""
    with pytest.raises(SystemExit) as error:
        main(["clear"])

    assert error.value.code == 2


def test_cli_clear_prints_deleted_count(monkeypatch, capsys) -> None:
    """The clear command should report how many chunks were removed."""
    monkeypatch.setattr("src.vector_store_utils.clear_vector_store", lambda: 3)

    exit_code = main(["clear", "--yes"])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"deleted_chunks": 3}
