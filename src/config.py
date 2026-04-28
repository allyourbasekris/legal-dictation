import os
import platform
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "legal-dictation"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

WHISPER_MODEL = "small.en"

_IS_WINDOWS = platform.system() == "Windows"
LLAMA_BINARY_NAME = "llama-cli.exe" if _IS_WINDOWS else "llama-cli"
LLAMA_BINARY_PATH = CACHE_DIR / LLAMA_BINARY_NAME
LLAMA_BINARY_URL = (
    "https://github.com/ggml-org/llama.cpp/releases/download/b4822/"
    + ("llama-b4822-bin-win-cuda-cu12.6-x64.zip" if _IS_WINDOWS else "llama-b4822-bin-ubuntu-x64.zip")
)

LLAMA_REPO = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
LLAMA_FILE = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
LLAMA_MODEL_PATH = CACHE_DIR / LLAMA_FILE
LLAMA_MODEL_URL = f"https://huggingface.co/{LLAMA_REPO}/resolve/main/{LLAMA_FILE}"

WHISPER_CACHE = CACHE_DIR / "whisper"
WHISPER_CACHE.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = Path.home() / "Documents"
