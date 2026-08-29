from pathlib import Path

from services.document_processing.storage import LocalFileStorage


PROJECT_ROOT = Path(__file__).resolve().parents[4]
STORAGE_ROOT = PROJECT_ROOT / "data" / "uploads"

file_storage = LocalFileStorage(STORAGE_ROOT)