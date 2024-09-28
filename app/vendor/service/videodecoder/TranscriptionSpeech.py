import re

from moviepy.audio.AudioClip import AudioClip

from .normalizator import normalize_name
import whisper

class TranscriptionSpeech:

    def __init__(self):
        self.model = whisper.load_model("tiny")

    def stt(self, filename: str):
        filename = normalize_name(filename)
        # TODO вынести путь до файлов в конфиг
        audio_text = self.model.transcribe("./output/audios/" + filename + ".mp3", language="ru")
        # TODO вынести путь до файлов в конфиг
        with open("./output/text/" + filename.lower() + ".txt", "w", encoding="utf-8") as file:
            file.write(audio_text["text"])
