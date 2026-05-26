"""Backend-only Chroma inspection and admin utilities.

CLI usage:
    uv run python -m src.vector_store_utils stats
    uv run python -m src.vector_store_utils list-metadata --limit 20
    uv run python -m src.vector_store_utils delete-source my_file.pdf --yes
    uv run python -m src.vector_store_utils clear --yes
"""

import argparse
import json
from typing import Any, Sequence

from src.utils import clear_ingested_hashes
from src.vector_store import get_vector_store


def _get_collection() -> Any:
    """Return the underlying Chroma collection for admin/debug operations."""
    return get_vector_store()._collection


def get_vector_store_stats() -> dict[str, Any]:
    """Return basic collection stats for inspection."""
    collection = _get_collection()
    payload = collection.get(include=["metadatas"])
    metadatas = payload.get("metadatas", [])
    sources = sorted(
        {
            metadata.get("source")
            for metadata in metadatas
            if metadata and metadata.get("source")
        }
    )

    return {
        "collection_name": collection.name,
        "total_chunks": collection.count(),
        "sources": sources,
    }


def list_chunk_metadata(limit: int = 50) -> list[dict[str, Any]]:
    """List stored chunk metadata without returning embeddings or chunk text."""
    collection = _get_collection()
    payload = collection.get(limit=limit, include=["metadatas"])
    ids = payload.get("ids", [])
    metadatas = payload.get("metadatas", [])
    rows: list[dict[str, Any]] = []

    for chunk_id, metadata in zip(ids, metadatas):
        metadata = metadata or {}
        rows.append(
            {
                "chunk_id": chunk_id,
                "source": metadata.get("source"),
                "page": metadata.get("page"),
                "chunk_index": metadata.get("chunk_index"),
            }
        )

    return rows

# Not Implmented because current hash log design does not allow safe cleanup of hashes when deleting by source.
def delete_chunks_by_source(source: str) -> int:
    """Delete every chunk for a source and return how many were removed."""
    # collection = _get_collection()
    # payload = collection.get(where={"source": source}, include=[])
    # ids = payload.get("ids", [])
    #
    # if ids:
    #     collection.delete(ids=ids)
    #     # We intentionally do not remove any entry from the hash log here yet.
    #     # The current log stores hashes only, without a source-to-hash mapping,
    #     # so we cannot safely determine which hash belongs to this source or
    #     # whether the same hash is still referenced by another ingested file.
    #
    # return len(ids)
    raise NotImplementedError(
        "delete_chunks_by_source is not implemented until hash-log and source "
        "tracking can be kept in sync."
    )


def clear_vector_store() -> int:
    """Delete all stored chunks and return how many were removed."""
    collection = _get_collection()
    count = collection.count()

    if count:
        payload = collection.get(include=[])
        ids = payload.get("ids", [])
        if ids:
            collection.delete(ids=ids)

    clear_ingested_hashes()

    return count


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for vector-store admin tasks."""
    parser = argparse.ArgumentParser(
        description="Inspect and manage the local Chroma vector store.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stats", help="Show collection stats.")

    list_parser = subparsers.add_parser(
        "list-metadata",
        help="List stored chunk metadata.",
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of chunk metadata rows to return.",
    )

    delete_parser = subparsers.add_parser(
        "delete-source",
        help="Delete all chunks that belong to one source file.",
    )
    delete_parser.add_argument("source", help="Source filename to delete.")
    delete_parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm deletion without an interactive prompt.",
    )

    clear_parser = subparsers.add_parser(
        "clear",
        help="Delete every chunk from the vector store.",
    )
    clear_parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm deletion without an interactive prompt.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the vector-store utility CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "stats":
        print(json.dumps(get_vector_store_stats(), indent=2))
        return 0

    if args.command == "list-metadata":
        print(json.dumps(list_chunk_metadata(limit=args.limit), indent=2))
        return 0

    if args.command == "delete-source":
        if not args.yes:
            parser.error("delete-source requires --yes to confirm deletion.")
        print(
            json.dumps(
                {
                    "source": args.source,
                    "deleted_chunks": delete_chunks_by_source(args.source),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "clear":
        if not args.yes:
            parser.error("clear requires --yes to confirm deletion.")
        print(
            json.dumps(
                {"deleted_chunks": clear_vector_store()},
                indent=2,
            )
        )
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
