import os
import subprocess
from src.config import LLAMA_BINARY_PATH, LLAMA_MODEL_PATH


def llama_complete(prompt, max_tokens=1024, temperature=0.1):
    binary = str(LLAMA_BINARY_PATH)
    model = str(LLAMA_MODEL_PATH)

    if not os.path.exists(binary):
        raise RuntimeError(f"llama-cli not found at {binary}. Run setup.bat to download it.")
    if not os.path.exists(model):
        raise RuntimeError(f"Model not found at {model}. It will be downloaded on first run.")

    cmd = [
        binary, "-m", model, "-p", prompt,
        "-n", str(max_tokens), "--temp", str(temperature),
        "--no-display-prompt", "-c", "4096",
        "--threads", str(os.cpu_count() or 4),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        raise RuntimeError(f"llama-cli error: {result.stderr.strip()}")

    return result.stdout.strip()


def correct_text(text):
    prompt = (
        "You are a legal text proofreading assistant. Fix grammar, spelling, and punctuation. "
        "Preserve all names, dates, case numbers, and legal terminology exactly. "
        "Output only the corrected text.\n\n"
        f"{text}"
    )
    return llama_complete(prompt, max_tokens=len(text) + 256, temperature=0.1)


def format_text(text):
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
    return llama_complete(prompt, max_tokens=len(text) + 512, temperature=0.2)
