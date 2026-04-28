import argparse
import time
import sys
from pathlib import Path

from src.log import log
from src.transcriber import Transcriber
from src import corrector
from src.formatter import build_docx, save_docx
from src.config import OUTPUT_DIR


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
    log.info("Starting pipeline...")
    t0 = time.time()

    wav_path = str(audio)
    cleanup = False
    if audio.suffix.lower() != ".wav":
        log.info("Converting to 16kHz mono WAV...")
        from pydub import AudioSegment
        aud = AudioSegment.from_file(str(audio))
        wav_path = str(audio.with_suffix(".converted.wav"))
        aud.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
        cleanup = True
        log.info(f"Duration: {len(aud) / 1000:.1f}s")

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
    log.info(raw[:500])

    if cleanup:
        try:
            Path(wav_path).unlink()
        except OSError:
            pass

    if not raw.strip():
        log.warning("No speech detected!")
        sys.exit(1)

    log.info("Processing punctuation & formatting...")
    t3 = time.time()
    corrected, formatted = corrector.process(raw)
    t4 = time.time()
    log.info(f"Processing done in {t4 - t3:.2f}s")
    log.info(f"Corrected: {len(corrected)} chars")
    log.info(f"Formatted output:")
    log.info(formatted)

    output_path = args.output or str(OUTPUT_DIR / f"transcription_{audio.stem}.docx")
    log.info(f"Saving .docx to {output_path}")
    doc = build_docx(raw, corrected, formatted, str(audio))
    save_docx(doc, output_path)

    t_end = time.time()
    log.info(f"Total time: {t_end - t0:.1f}s")
    log.info("Done!")


if __name__ == "__main__":
    main()
