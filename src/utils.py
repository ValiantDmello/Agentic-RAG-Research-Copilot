import hashlib
from pathlib import Path


HASH_LOG = Path("data/ingested_hashes.txt")


def file_hash(file_path: str) -> str:
    """Return a SHA-256 hash for the file contents."""
    path = Path(file_path)
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(8192), b""):
            digest.update(block)

    return digest.hexdigest()


def already_ingested(hash_value: str) -> bool:
    """Return whether the file hash has already been recorded."""
    if not HASH_LOG.exists():
        return False

    return hash_value in HASH_LOG.read_text(encoding="utf-8").splitlines()


def record_ingested(hash_value: str) -> None:
    """Append a successfully ingested file hash to the local log."""
    HASH_LOG.parent.mkdir(parents=True, exist_ok=True)

    with HASH_LOG.open("a", encoding="utf-8") as file:
        file.write(hash_value + "\n")


def clear_ingested_hashes() -> None:
    """Remove the duplicate-ingestion hash log if it exists."""
    if HASH_LOG.exists():
        HASH_LOG.unlink()
