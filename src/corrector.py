import os
import subprocess
import threading
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


def _reader_thread(stream, out_list, done_event):
    buf = []
    while True:
        chunk = stream.read(4096)
        if not chunk:
            break
        buf.append(chunk)
        out_list.append(chunk)
    out_list.append("".join(buf))
    done_event.set()


def llama_complete(prompt, max_tokens=1024, temperature=0.1, on_token=None):
    binary = str(LLAMA_BINARY_PATH)
    model = str(LLAMA_MODEL_PATH)

    if not os.path.exists(binary):
        raise RuntimeError(f"llama-cli not found at {binary}. Run setup.bat.")
    if not os.path.exists(model):
        raise RuntimeError(f"Model not found at {model}.")

    cmd = [
        binary, "-m", model, "-p", prompt,
        "-n", str(max_tokens), "--temp", str(temperature),
        "--no-display-prompt", "-c", "4096",
        "--threads", str(os.cpu_count() or 4),
    ]

    if on_token:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        chunks = []
        done = threading.Event()
        t = threading.Thread(target=_reader_thread, args=(proc.stdout, chunks, done), daemon=True)
        t.start()
        idx = 0
        while not done.is_set() or idx < len(chunks):
            done.wait(0.05)
            while idx < len(chunks):
                on_token(chunks[idx])
                idx += 1
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("llama-cli failed")
        full = "".join(chunks)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"llama-cli error: {result.stderr.strip()[:500]}")
        full = result.stdout

    for token in ["<|im_end|>", "<|endoftext|>"]:
        if full.rstrip().endswith(token):
            full = full[: -len(token)].rstrip()
    return full.strip()


def correct_text(text, on_token=None):
    return llama_complete(
        _build_prompt(QWEN_SYSTEM, f"Correct this text:\n\n{text}"),
        max_tokens=len(text) + 256,
        temperature=0.1,
        on_token=on_token,
    )


def format_text(text, on_token=None):
    return llama_complete(
        _build_prompt(QWEN_FORMAT_SYSTEM, f"Format into sections:\n\n{text}"),
        max_tokens=len(text) + 512,
        temperature=0.2,
        on_token=on_token,
    )
