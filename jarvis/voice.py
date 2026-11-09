"""
Voice Engine — Speech Recognition + Text-to-Speech
"""

import speech_recognition as sr
import pyttsx3
from typing import Optional


class VoiceEngine:
    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts = self._setup_tts()

    def _setup_tts(self):
        """TTS engine initialize করো"""
        engine = pyttsx3.init()
        engine.setProperty("rate", self.config.tts_rate)
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        return engine

    def speak(self, text: str):
        """Jarvis কথা বলবে"""
        print(f"\n🤖 {self.config.assistant_name}: {text}\n")
        self.tts.say(text)
        self.tts.runAndWait()

    def listen(self) -> Optional[str]:
        """Microphone থেকে voice শুনবে"""
        print("🎤 শুনছি...")

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=self.config.mic_timeout,
                    phrase_time_limit=self.config.mic_phrase_limit
                )
            except sr.WaitTimeoutError:
                return None

        try:
            text = self.recognizer.recognize_google(
                audio,
                language=self.config.speech_language
            )
            print(f"👤 আপনি: {text}")
            return text.lower()

        except sr.UnknownValueError:
            print("❓ বুঝতে পারিনি।")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            return None
