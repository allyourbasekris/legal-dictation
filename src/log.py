import logging
import sys
from pathlib import Path

LOG_DIR = Path.home() / ".cache" / "legal-dictation" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "legal-dictation.log"

_file_handler = logging.FileHandler(str(LOG_FILE), mode="w", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

_logger = logging.getLogger("legal-dictation")
_logger.setLevel(logging.DEBUG)
_logger.addHandler(_file_handler)
_logger.addHandler(_console_handler)

log = _logger
log.info(f"Logging to {LOG_FILE}")
