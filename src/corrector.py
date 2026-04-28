import os, subprocess, logging
from src.config import LLAMA_BINARY_PATH, LLAMA_MODEL_PATH

QWEN_SYSTEM = (
    "You are a legal text proofreading and formatting assistant. "
    "Fix grammar, spelling, and punctuation. Preserve names, dates, case numbers, "
    "and legal terminology exactly. Be concise."
)

QWEN_FORMAT_SYSTEM = (
    "You classify legal dictation into sections. "
    "Use these exact headers: === FILE NOTES ===, === TIME RECORDING ===, "
    "=== CORRESPONDENCE ===, === ACTION ITEMS ===. "
    "For ACTION ITEMS use [ ] checkboxes. "
    "Only include sections that are present in the text. "
    "If the entire content is one type, use just that single header. Be concise."
)


def _build_prompt(system, user_text):
    return (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{user_text}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


def llama_complete(prompt, max_tokens=1024, temperature=0.1):
    binary = str(LLAMA_BINARY_PATH)
    model = str(LLAMA_MODEL_PATH)

    if not os.path.exists(binary):
        raise RuntimeError(f"llama-cli not found at {binary}.")
    if not os.path.exists(model):
        raise RuntimeError(f"Model not found at {model}.")

    log = logging.getLogger("legal-dictation")
    log.info(f"LLM input prompt length: {len(prompt)} chars, max_tokens={max_tokens}")

    # -p with --single-turn prevents interactive mode and exits after generation
    # subprocess.run passes args directly via CreateProcess, no cmd.exe shell quoting issues
    cmd = [
        binary, "-m", model,
        "-p", prompt,
        "-n", str(max_tokens), "--temp", str(temperature),
        "--no-display-prompt", "--single-turn",
        "-c", "4096",
        "--threads", str(os.cpu_count() or 4),
    ]

    log.info(f"Running llama-cli...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)

    if result.returncode != 0:
        err = result.stderr.strip()[:500]
        log.error(f"llama-cli stderr: {err}")
        raise RuntimeError(f"llama-cli error: {err}")

    full = result.stdout
    log.info(f"LLM output length: {len(full)} chars")

    for token in ["<|im_end|>", "<|endoftext|>"]:
        if full.rstrip().endswith(token):
            full = full[: -len(token)].rstrip()
    return full.strip()


def correct_text(text):
    prompt = _build_prompt(QWEN_SYSTEM, f"Correct this text:\n\n{text}")
    return llama_complete(prompt, max_tokens=len(text) + 256, temperature=0.1)


def format_text(text):
    prompt = _build_prompt(QWEN_FORMAT_SYSTEM, f"Format into sections:\n\n{text}")
    return llama_complete(prompt, max_tokens=len(text) + 512, temperature=0.2)
