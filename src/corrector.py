import os
import requests
from pathlib import Path
from src.config import LLAMA_PATH, LLAMA_HF_URL

_MODEL_INSTANCE = None


def _download_progress(url, dest, callback=None):
    dest = Path(dest)
    if dest.exists():
        if callback:
            callback(1.0)
        return
    tmp = dest.with_suffix(".part")
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(tmp, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if callback and total:
                callback(downloaded / total)
    tmp.rename(dest)


def download_model(callback=None):
    _download_progress(LLAMA_HF_URL, LLAMA_PATH, callback)
    return LLAMA_PATH


def load_model(n_ctx=4096, n_threads=None):
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is not None:
        return _MODEL_INSTANCE
    from llama_cpp import Llama
    _MODEL_INSTANCE = Llama(
        model_path=str(LLAMA_PATH),
        n_ctx=n_ctx,
        n_threads=n_threads or os.cpu_count() or 4,
        verbose=False,
    )
    return _MODEL_INSTANCE


def unload_model():
    global _MODEL_INSTANCE
    _MODEL_INSTANCE = None


def correct_text(text):
    llm = load_model()
    prompt = (
        "You are a legal text proofreading assistant. Fix grammar, spelling, and punctuation. "
        "Preserve all names, dates, case numbers, and legal terminology exactly. "
        "Output only the corrected text.\n\n"
        f"{text}"
    )
    result = llm.create_completion(prompt, max_tokens=len(text) + 256, temperature=0.1, stop=None)
    return result["choices"][0]["text"].strip()


def format_text(text):
    llm = load_model()
    prompt = (
        "Classify the following legal dictation into sections. Only include sections that are present. "
        "Use these exact headers:\n"
        "=== FILE NOTES ===\n"
        "=== TIME RECORDING ===\n"
        "=== CORRESPONDENCE ===\n"
        "=== ACTION ITEMS ===\n\n"
        "For ACTION ITEMS use checkboxes like: [ ] Task description\n"
        "If the entire content is one type, use just that single header.\n\n"
        f"{text}"
    )
    result = llm.create_completion(prompt, max_tokens=len(text) + 512, temperature=0.2, stop=None)
    return result["choices"][0]["text"].strip()
