import os, subprocess, logging, tempfile, uuid, re
from pathlib import Path
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


def _strip_banner(text):
    """Remove llama-cli's banner, prompt echo, and trailing stats from output."""
    # Find the last "> " prompt marker — everything before it is banner/echo
    idx = text.rfind("> ")
    if idx != -1:
        text = text[idx + 2:].lstrip("\n")

    # Strip trailing lines starting with common metadata markers
    text = re.sub(
        r'\n(?:\[ Prompt: .*|common_memory_breakdown.*|Exiting\.\.\.|\s*$)',
        '',
        text,
    )

    # Strip special tokens
    for token in ["<|im_end|>", "<|endoftext|>"]:
        if text.rstrip().endswith(token):
            text = text[: -len(token)].rstrip()

    return text.strip()


def llama_complete(prompt, max_tokens=1024, temperature=0.1):
    binary = str(LLAMA_BINARY_PATH)
    model = str(LLAMA_MODEL_PATH)

    if not os.path.exists(binary):
        raise RuntimeError(f"llama-cli not found at {binary}.")
    if not os.path.exists(model):
        raise RuntimeError(f"Model not found at {model}.")

    log = logging.getLogger("legal-dictation")
    log.info(f"LLM input prompt len={len(prompt)} max_tokens={max_tokens}")

    # Write prompt to temp file, use --file to avoid shell quoting
    prompt_file = Path(tempfile.gettempdir()) / f"llama_prompt_{uuid.uuid4().hex}.txt"
    prompt_file.write_text(prompt, encoding="utf-8")

    cmd = [
        binary, "-m", model,
        "--file", str(prompt_file),
        "-n", str(max_tokens), "--temp", str(temperature),
        "--no-display-prompt", "--single-turn",
        "-c", "4096",
        "--threads", str(os.cpu_count() or 4),
    ]

    # Close stdin immediately so llama-cli exits after processing the file
    result = subprocess.run(cmd, input="", capture_output=True, text=True, timeout=1200)

    try:
        prompt_file.unlink()
    except OSError:
        pass

    if result.returncode != 0:
        raise RuntimeError(f"llama-cli error: {result.stderr.strip()[:500]}")

    full = _strip_banner(result.stdout)
    log.info(f"Output: {len(full)} chars")
    return full


def correct_text(text):
    return llama_complete(
        _build_prompt(QWEN_SYSTEM, f"Correct this text:\n\n{text}"),
        max_tokens=len(text) + 256, temperature=0.1,
    )


def format_text(text):
    return llama_complete(
        _build_prompt(QWEN_FORMAT_SYSTEM, f"Format into sections:\n\n{text}"),
        max_tokens=len(text) + 512, temperature=0.2,
    )
