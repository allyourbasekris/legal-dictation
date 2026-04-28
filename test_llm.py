"""Test just the LLM correction/formatting without re-transcribing.

Usage:
  python test_llm.py "path/to/transcript.txt"           # from file
  python test_llm.py --correct "Some text to correct"       # inline
  python test_llm.py --format "Some text to format"         # inline
  python test_llm.py "transcript.txt" --all                 # both passes
"""
import argparse
import sys
from pathlib import Path

from src import corrector
from src.log import log


def main():
    parser = argparse.ArgumentParser(description="Test LLM correction/formatting")
    parser.add_argument("input", nargs="?", help="Text file or inline text")
    parser.add_argument("--correct", action="store_true", help="Run grammar correction")
    parser.add_argument("--format", action="store_true", help="Run formatting")
    parser.add_argument("--all", action="store_true", help="Run both correction and formatting")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    # Read input
    p = Path(args.input)
    if p.exists():
        text = p.read_text(encoding="utf-8")
        log.info(f"Read {len(text)} chars from {p}")
    else:
        text = args.input
        log.info(f"Inline text: {len(text)} chars")

    if not text.strip():
        log.error("Empty input")
        sys.exit(1)

    log.info(f"Text preview: {text[:200]}...")

    do_correct = args.correct or args.all
    do_format = args.format or args.all
    if not do_correct and not do_format:
        do_correct = do_format = True

    if do_correct:
        log.info("=" * 60)
        log.info("PHASE 1: Grammar Correction")
        log.info("=" * 60)
        try:
            corrected = corrector.correct_text(text)
            log.info(f"Output ({len(corrected)} chars):")
            log.info(corrected)
        except Exception as e:
            log.error(f"Correction failed: {e}")

    if do_format:
        source = corrected if (do_correct and 'corrected' in dir()) else text
        log.info("=" * 60)
        log.info("PHASE 2: Formatting")
        log.info("=" * 60)
        try:
            formatted = corrector.format_text(source)
            log.info(f"Output ({len(formatted)} chars):")
            log.info(formatted)
        except Exception as e:
            log.error(f"Formatting failed: {e}")

    log.info("Done.")


if __name__ == "__main__":
    main()
