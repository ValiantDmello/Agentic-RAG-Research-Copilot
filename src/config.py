import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")