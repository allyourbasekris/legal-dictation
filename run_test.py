"""Run the full pipeline on a single audio file, no GUI. For debugging."""
import argparse
import time
import sys
from pathlib import Path

from src.log import log
from src.transcriber import Transcriber
from src import corrector
from src.formatter import build_docx, save_docx
from src.downloader import _download_progress
from src.config import LLAMA_MODEL_PATH, LLAMA_BINARY_PATH, OUTPUT_DIR


def main():
    parser = argparse.ArgumentParser(description="Test dictation pipeline")
    parser.add_argument("audio", help="Path to audio file")
    parser.add_argument("--output", "-o", help="Output .docx path (optional)")
    args = parser.parse_args()

    audio = Path(args.audio)
    if not audio.exists():
        log.error(f"File not found: {audio}")
        sys.exit(1)

    log.info(f"Audio file: {audio}")
    log.info(f"File size: {audio.stat().st_size / 1024:.1f} KB")

    # Check models
    log.info(f"llama-cli: {'FOUND' if LLAMA_BINARY_PATH.exists() else 'MISSING'} at {LLAMA_BINARY_PATH}")
    log.info(f"GGUF model: {'FOUND' if LLAMA_MODEL_PATH.exists() else 'MISSING'} at {LLAMA_MODEL_PATH}")

    if not LLAMA_MODEL_PATH.exists():
        log.info("Downloading LLM model (1 GB)...")
        _download_progress(
            "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            LLAMA_MODEL_PATH,
            callback=lambda p: print(f"\rDownloading LLM: {p:.0%}", end="", flush=True),
        )
        print()

    log.info("Starting pipeline...")
    t0 = time.time()

    # --- Step 1: Convert if needed ---
    wav_path = str(audio)
    cleanup = False
    if audio.suffix.lower() != ".wav":
        log.info("Converting to 16kHz mono WAV...")
        from pydub import AudioSegment
        aud = AudioSegment.from_file(str(audio))
        wav_path = str(audio.with_suffix(".converted.wav"))
        aud.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
        cleanup = True
        log.info(f"Converted to {wav_path}")
        log.info(f"Duration: {len(aud) / 1000:.1f}s")

    # --- Step 2: Transcribe ---
    log.info("Loading Whisper model...")
    transcriber = Transcriber()
    t1 = time.time()
    log.info(f"Whisper loaded in {t1 - t0:.1f}s")

    log.info("Transcribing...")
    raw, lang, prob = transcriber.transcribe(wav_path)
    t2 = time.time()
    log.info(f"Transcription done in {t2 - t1:.1f}s")
    log.info(f"Detected language: {lang} (confidence: {prob:.2f})")
    log.info(f"Raw text ({len(raw)} chars):")
    log.info("-" * 60)
    for line in raw.split(". "):
        log.info(f"  {line.strip()}.")
    log.info("-" * 60)

    if cleanup:
        try:
            Path(wav_path).unlink()
        except OSError:
            pass

    if not raw.strip():
        log.warning("No speech detected!")
        sys.exit(1)

    # --- Step 3: Correct grammar ---
    log.info("Correcting grammar...")
    t3 = time.time()
    try:
        corrected = corrector.correct_text(raw)
        t4 = time.time()
        log.info(f"Grammar correction done in {t4 - t3:.1f}s")
        log.info(f"Corrected text ({len(corrected)} chars):")
        log.info("-" * 60)
        log.info(corrected)
        log.info("-" * 60)
    except Exception as e:
        log.error(f"Grammar correction FAILED: {e}")
        corrected = raw

    # --- Step 4: Format ---
    log.info("Formatting into sections...")
    t5 = time.time()
    try:
        formatted = corrector.format_text(corrected)
        t6 = time.time()
        log.info(f"Formatting done in {t6 - t5:.1f}s")
        log.info(f"Formatted output:")
        log.info("*" * 60)
        log.info(formatted)
        log.info("*" * 60)
    except Exception as e:
        log.error(f"Formatting FAILED: {e}")
        formatted = corrected

    # --- Step 5: Save .docx ---
    output_path = args.output or str(OUTPUT_DIR / f"transcription_{audio.stem}.docx")
    log.info(f"Saving .docx to {output_path}")
    doc = build_docx(raw, corrected, formatted, str(audio))
    save_docx(doc, output_path)

    t_end = time.time()
    log.info(f"Total time: {t_end - t0:.1f}s")
    log.info("Done!")


if __name__ == "__main__":
    main()
