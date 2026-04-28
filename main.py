import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import logging
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import platform
import subprocess
from pathlib import Path
from datetime import datetime

from src.transcriber import Transcriber
from src import corrector
from src.downloader import _download_progress
from src.formatter import build_docx, save_docx
from src.config import OUTPUT_DIR, LLAMA_MODEL_PATH, LLAMA_BINARY_PATH


class LegalDictationApp:
    def __init__(self, root):
        self.root = root
        root.title("Legal Dictation Tool")
        root.geometry("1000x700")
        root.minsize(800, 500)

        self.audio_path = None
        self.raw_text = ""
        self.corrected_text = ""
        self.formatted_text = ""
        self.doc = None

        self._build_ui()
        self._bind_shortcuts()
        self._check_models()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        file_frame = ttk.LabelFrame(main, text="Audio File", padding=8)
        file_frame.pack(fill=tk.X, pady=(0, 8))

        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(file_frame, text="Browse...", command=self._browse_file).pack(side=tk.RIGHT, padx=(8, 0))

        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(0, 8))

        self.start_btn = ttk.Button(action_frame, text="Transcribe & Format", command=self._start_pipeline, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(action_frame, mode="indeterminate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(action_frame, textvariable=self.status_var, width=30)
        status_label.pack(side=tk.RIGHT, padx=(4, 0))

        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(paned, text="Raw Transcription", padding=4)
        self.raw_text_widget = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10))
        self.raw_text_widget.pack(fill=tk.BOTH, expand=True)
        paned.add(left_frame, weight=1)

        right_frame = ttk.LabelFrame(paned, text="Formatted Output", padding=4)
        self.formatted_text_widget = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10))
        self.formatted_text_widget.pack(fill=tk.BOTH, expand=True)
        paned.add(right_frame, weight=1)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(btn_frame, text="Save as .docx", command=self._save_docx).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Copy Raw", command=lambda: self._copy_text(self.raw_text_widget)).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Copy Formatted", command=lambda: self._copy_text(self.formatted_text_widget)).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side=tk.RIGHT)

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self._browse_file())
        self.root.bind("<Control-Return>", lambda e: self._start_pipeline())
        self.root.bind("<Control-s>", lambda e: self._save_docx())

    def _check_models(self):
        self.start_btn.config(state=tk.DISABLED)
        if not LLAMA_BINARY_PATH.exists():
            self.status_var.set(f"llama-cli not found. Run setup.bat to download it.")
            return
        if not LLAMA_MODEL_PATH.exists():
            self.status_var.set("Downloading LLM model (1 GB) on first use...")
            threading.Thread(target=self._download_llm, daemon=True).start()
        else:
            self.status_var.set("Ready")

    def _download_llm(self):
        try:
            _download_progress(
                "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
                LLAMA_MODEL_PATH,
                callback=lambda p: self.root.after(0, lambda: self.status_var.set(f"Downloading LLM: {p:.0%}"))
            )
            self.root.after(0, lambda: self.status_var.set("Ready"))
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL if self.audio_path else tk.DISABLED))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Download Error", f"Failed to download LLM model:\n{e}"))
            self.root.after(0, lambda: self.status_var.set("Download failed"))

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.wav *.mp3 *.m4a *.ogg *.flac *.aac"), ("All files", "*.*")]
        )
        if path:
            self.audio_path = path
            self.file_label.config(text=os.path.basename(path))
            self.start_btn.config(state=tk.NORMAL)

    def _set_text(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state=tk.DISABLED)

    def _append_text(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.insert(tk.END, text)
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)

    def _copy_text(self, widget):
        text = widget.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)

    def _clear(self):
        self.audio_path = None
        self.raw_text = ""
        self.corrected_text = ""
        self.formatted_text = ""
        self.doc = None
        self.file_label.config(text="No file selected")
        self._set_text(self.raw_text_widget, "")
        self._set_text(self.formatted_text_widget, "")
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set("Ready")

    def _start_pipeline(self):
        if not self.audio_path:
            return
        self.start_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        threading.Thread(target=self._run_pipeline, daemon=True).start()

    def _run_pipeline(self):
        try:
            wav_path = self.audio_path
            ext = os.path.splitext(wav_path)[1].lower()
            cleanup = False
            if ext != ".wav":
                self.root.after(0, lambda: self.status_var.set("Converting audio..."))
                from pydub import AudioSegment
                audio = AudioSegment.from_file(wav_path)
                wav_path = wav_path + ".converted.wav"
                audio.export(wav_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
                cleanup = True

            self.root.after(0, lambda: self.status_var.set("Transcribing..."))
            transcriber = Transcriber()

            self.root.after(0, lambda: self._set_text(self.raw_text_widget, ""))

            raw = ""
            def on_segment(text):
                nonlocal raw
                raw += text + " "
                self.root.after(0, lambda t=text: self._append_text(self.raw_text_widget, t + " "))

            full_raw, lang, prob = transcriber.transcribe(wav_path, on_segment=on_segment)
            raw = full_raw

            if cleanup:
                try:
                    os.remove(wav_path)
                except OSError:
                    pass

            if not raw.strip():
                self.root.after(0, lambda: messagebox.showwarning("No Speech", "No speech detected in audio."))
                return

            self.raw_text = raw
            self.root.after(0, lambda: self._set_text(self.raw_text_widget, raw))

            self.root.after(0, lambda: self._set_text(self.formatted_text_widget, "=== GRAMMAR CORRECTION ===\n\n"))
            self.root.after(0, lambda: self.status_var.set("Correcting grammar..."))
            corrected = corrector.correct_text(raw)
            self.corrected_text = corrected
            self.root.after(0, lambda: self._append_text(self.formatted_text_widget, corrected + "\n\n"))

            self.root.after(0, lambda: self.status_var.set("Formatting document..."))
            formatted = corrector.format_text(corrected)
            self.formatted_text = formatted
            self.root.after(0, lambda: self._append_text(self.formatted_text_widget, "=== FORMATTING ===\n\n" + formatted))

            self.doc = build_docx(raw, corrected, formatted, self.audio_path)

            self.root.after(0, lambda: self.status_var.set("Complete"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.status_var.set("Error"))
        finally:
            self.root.after(0, self._pipeline_done)

    def _pipeline_done(self):
        self.progress.stop()
        self.start_btn.config(state=tk.NORMAL if self.audio_path else tk.DISABLED)

    def _save_docx(self):
        if self.doc is None:
            messagebox.showinfo("No Document", "Process an audio file first.")
            return
        default_name = f"transcription_{Path(self.audio_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        path = filedialog.asksaveasfilename(
            title="Save Document",
            initialdir=str(OUTPUT_DIR),
            initialfile=default_name,
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")]
        )
        if not path:
            return
        save_docx(self.doc, path)
        if platform.system() == "Darwin":
            subprocess.run(["open", path], check=False)
        elif platform.system() == "Windows":
            os.startfile(path)
        else:
            subprocess.run(["xdg-open", path], check=False)


def main():
    root = tk.Tk()
    app = LegalDictationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
