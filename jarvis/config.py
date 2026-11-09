"""
Jarvis Configuration
সব settings এখানে — একটা জায়গা থেকে সব control করা যাবে
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    # ── AI Settings ─────────────────────────────────────────────────────────
    # OpenAI key: https://platform.openai.com/api-keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

    # AI Model — gpt-3.5-turbo (সস্তা) বা gpt-4 (ভালো)
    ai_model: str = "gpt-3.5-turbo"

    # AI-এর character
    ai_system_prompt: str = """তুমি Jarvis, একজন বুদ্ধিমান AI assistant।
তুমি PC এবং Android phone দুটোই control করতে পারো।
উত্তর সংক্ষিপ্ত রাখো (২-৩ বাক্য)।
বাংলা ও ইংরেজি দুটোতেই কথা বলতে পারো।
তুমি helpful, friendly এবং efficient।"""

    # ── Voice Settings ───────────────────────────────────────────────────────
    # Speech recognition language: "bn-BD" বা "en-US"
    speech_language: str = "bn-BD"

    # TTS speed (100-200)
    tts_rate: int = 160

    # Microphone timeout (seconds)
    mic_timeout: int = 5
    mic_phrase_limit: int = 10

    # ── Android / ADB Settings ───────────────────────────────────────────────
    # Windows: r"C:\platform-tools\adb.exe"
    # Mac/Linux: "adb"
    adb_path: str = "adb"

    # ── App Settings ─────────────────────────────────────────────────────────
    assistant_name: str = "Jarvis"
    wake_word: str = "jarvis"

    # Conversation history max length
    max_history: int = 20

    # ── Android App Packages ─────────────────────────────────────────────────
    app_packages: dict = field(default_factory=lambda: {
        # Social Media
        "whatsapp": "com.whatsapp",
        "facebook": "com.facebook.katana",
        "instagram": "com.instagram.android",
        "youtube": "com.google.android.youtube",
        "tiktok": "com.zhiliaoapp.musically",
        "twitter": "com.twitter.android",
        "telegram": "org.telegram.messenger",
        "snapchat": "com.snapchat.android",
        "linkedin": "com.linkedin.android",
        "discord": "com.discord",
        "viber": "com.viber.voip",

        # Google Apps
        "gmail": "com.google.android.gm",
        "maps": "com.google.android.apps.maps",
        "chrome": "com.android.chrome",
        "camera": "com.android.camera2",
        "photos": "com.google.android.apps.photos",
        "drive": "com.google.android.apps.docs",
        "meet": "com.google.android.apps.meetings",
        "translate": "com.google.android.apps.translate",
        "news": "com.google.android.apps.magazines",
        "pay": "com.google.android.apps.nbu.paisa.user",

        # Music & Entertainment
        "spotify": "com.spotify.music",
        "youtube music": "com.google.android.apps.youtube.music",
        "netflix": "com.netflix.mediaclient",
        "prime video": "com.amazon.avod.thirdpartyclient",

        # System Apps
        "settings": "com.android.settings",
        "phone": "com.android.dialer",
        "contacts": "com.android.contacts",
        "messages": "com.android.mms",
        "calculator": "com.android.calculator2",
        "clock": "com.android.deskclock",
        "calendar": "com.android.calendar",
        "files": "com.android.documentsui",
        "play store": "com.android.vending",
        "music": "com.android.music",

        # Bangladesh Specific
        "bkash": "com.bKash.customerapp",
        "nagad": "merchant.com.dfs.nagad",
        "rocket": "com.dutchbanglabank.mobilebanking",
        "pathao": "com.pathao.user",
        "shohoz": "com.shohoz.app",
        "bikroy": "com.bikroy",
    })

    @property
    def ai_enabled(self) -> bool:
        return self.openai_api_key != "YOUR_OPENAI_API_KEY_HERE"
