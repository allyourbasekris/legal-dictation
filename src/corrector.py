import os, subprocess, logging, re, tempfile, uuid
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


def _strip_output(text):
    # Find the last prompt marker
    idx = text.rfind("\n> ")
    if idx >= 0:
        text = text[idx + 3:]

    # Find the last assistant marker (generation starts here)
    asst = text.rfind("<|im_start|>assistant")
    if asst >= 0:
        text = text[asst + len("<|im_start|>assistant"):]

    # Strip ANSI escape codes (colors)
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    # Strip trailing metadata
    text = re.sub(r'\n\[ Prompt: .*', '', text)
    text = re.sub(r'\ncommon_memory_breakdown.*', '', text)
    text = re.sub(r'\nExiting\.\.\..*', '', text)
    text = re.sub(r'<\|im_end\|>\s*$', '', text)
    text = re.sub(r'<\|endoftext\|>\s*$', '', text)
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

    # Write prompt and output to files to avoid pipe buffer deadlock
    uid = uuid.uuid4().hex[:8]
    tmp = Path(tempfile.gettempdir())
    prompt_file = tmp / f"llama_in_{uid}.txt"
    out_file = tmp / f"llama_out_{uid}.txt"

    prompt_file.write_text(prompt, encoding="utf-8")

    cmd = [
        binary, "-m", model,
        "-f", str(prompt_file),
        "-n", str(max_tokens), "--temp", str(temperature),
        "--no-display-prompt", "--single-turn",
        "-c", "4096",
        "--threads", str(os.cpu_count() or 4),
    ]

    # Write stdout directly to file and stderr to null to avoid pipe buffering issues
    with open(out_file, "w", encoding="utf-8") as fout:
        with open(os.devnull, "w") as ferr:
            result = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=fout, stderr=ferr, timeout=1200)

    try:
        prompt_file.unlink()
    except OSError:
        pass

    if result.returncode != 0:
        raise RuntimeError(f"llama-cli returned code {result.returncode}")

    full = out_file.read_text(encoding="utf-8")
    try:
        out_file.unlink()
    except OSError:
        pass

    log.info(f"Raw stdout: {len(full)} chars")
    full = _strip_output(full)
    log.info(f"Stripped: {len(full)} chars")
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
