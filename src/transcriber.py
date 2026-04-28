import os
from faster_whisper import WhisperModel
from src.config import WHISPER_MODEL, WHISPER_CACHE


class Transcriber:
    def __init__(self, model_size=None, device="cpu", compute_type="int8"):
        self.model_size = model_size or WHISPER_MODEL
        self.device = device
        self.compute_type = compute_type
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=str(WHISPER_CACHE),
            )
        return self._model

    def transcribe(self, audio_path, on_segment=None):
        segments, info = self.model.transcribe(audio_path, beam_size=5, word_timestamps=False)
        lang = info.language
        prob = info.language_probability

        text_parts = []
        for seg in segments:
            text_parts.append(seg.text.strip())
            if on_segment:
                on_segment(seg.text.strip())

        full = " ".join(text_parts)
        return full.strip(), lang, prob
