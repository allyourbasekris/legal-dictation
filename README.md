# Legal Dictation Tool

Offline legal transcription with punctuation correction and section formatting. CPU-only, no GPU, no LLM required.

## Features

- Transcribe audio files (mp3, wav, m4a, etc.) using faster-whisper (small.en, ~466 MB)
- Punctuation, capitalization, and sentence splitting via pysbd
- Auto-detects dictation sections: FILE NOTES, TIME RECORDING, CORRESPONDENCE, ACTION ITEMS
- Outputs formatted .docx documents
- Fully offline after first-run model download (~466 MB)
- Fast: no LLM inference, processing completes in seconds

## Requirements

- Python 3.10+
- ~2 GB RAM
- ~500 MB free disk (Whisper model)
- ffmpeg (for non-WAV audio files)

## Quick Start

### Windows
Double-click `setup.bat` — it checks prerequisites, creates a venv, installs deps, and launches the app.

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

The Whisper model downloads automatically on first run (~466 MB). Select an audio file, click "Transcribe & Format", and save the result as .docx.

## Keyboard Shortcuts

- `Ctrl+O` — Browse for audio file
- `Ctrl+Enter` — Start transcription
- `Ctrl+S` — Save .docx
