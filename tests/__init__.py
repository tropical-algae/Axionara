import os
from pathlib import Path

TEMP_SQLITE_FILEPATH: Path = Path("cache") / "temp_sqlite.db"
os.environ["SQL_DATABASE_URI"] = f"sqlite+aiosqlite:///{TEMP_SQLITE_FILEPATH}"

if TEMP_SQLITE_FILEPATH.exists():
    TEMP_SQLITE_FILEPATH.unlink()

TEMP_SQLITE_FILEPATH.parent.mkdir(parents=True, exist_ok=True)
