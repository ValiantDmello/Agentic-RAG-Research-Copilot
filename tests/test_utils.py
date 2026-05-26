from pathlib import Path

import src.utils as utils


def test_file_hash_matches_for_identical_content(tmp_path: Path) -> None:
    """Identical file contents should produce the same SHA-256 hash."""
    first_file = tmp_path / "first.txt"
    second_file = tmp_path / "second.txt"
    content = "duplicate-content-check\n"

    first_file.write_text(content, encoding="utf-8")
    second_file.write_text(content, encoding="utf-8")

    assert utils.file_hash(str(first_file)) == utils.file_hash(str(second_file))


def test_file_hash_differs_for_different_content(tmp_path: Path) -> None:
    """Different file contents should produce different hashes."""
    first_file = tmp_path / "first.txt"
    second_file = tmp_path / "second.txt"

    first_file.write_text("alpha\n", encoding="utf-8")
    second_file.write_text("beta\n", encoding="utf-8")

    assert utils.file_hash(str(first_file)) != utils.file_hash(str(second_file))


def test_record_ingested_makes_hash_detectable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Recording a hash should create the log file and allow future lookups."""
    hash_log = tmp_path / "ingested_hashes.txt"
    monkeypatch.setattr(utils, "HASH_LOG", hash_log)

    assert utils.already_ingested("abc123") is False

    utils.record_ingested("abc123")

    assert hash_log.exists()
    assert utils.already_ingested("abc123") is True
    assert utils.already_ingested("different-hash") is False
