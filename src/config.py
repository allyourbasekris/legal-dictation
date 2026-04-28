import platform
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "legal-dictation"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

WHISPER_MODEL = "small.en"
WHISPER_CACHE = CACHE_DIR / "whisper"
WHISPER_CACHE.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = Path.home() / "Documents"
