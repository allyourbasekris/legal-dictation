# Legal Dictation Tool

Offline legal transcription with grammar correction and document formatting, powered by Whisper + LLM. CPU-only, no GPU required.

## Features

- Transcribe audio files (mp3, wav, m4a, etc.) using faster-whisper
- Grammar and spell check via local LLM (Qwen2.5-1.5B, ~1 GB GGUF)
- Auto-classifies dictation into sections: FILE NOTES, TIME RECORDING, CORRESPONDENCE, ACTION ITEMS
- Outputs formatted .docx documents
- Fully offline after first-run model download (~1.5 GB total)
- Uses llama.cpp binary — no C++ compiler or `llama-cpp-python` needed

## Requirements

- Python 3.10+
- ~4 GB RAM
- ~2 GB free disk for models
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

Models download automatically on first run (~1.5 GB total). Select an audio file, click "Transcribe & Format", and save the result as .docx.

## Keyboard Shortcuts

- `Ctrl+O` — Browse for audio file
- `Ctrl+Enter` — Start transcription
- `Ctrl+S` — Save .docx
