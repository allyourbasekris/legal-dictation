import os
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "legal-dictation"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

WHISPER_MODEL = "small.en"

LLAMA_REPO = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
LLAMA_FILE = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
LLAMA_PATH = CACHE_DIR / LLAMA_FILE
LLAMA_HF_URL = f"https://huggingface.co/{LLAMA_REPO}/resolve/main/{LLAMA_FILE}"

WHISPER_CACHE = CACHE_DIR / "whisper"
WHISPER_CACHE.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = Path.home() / "Documents"
