"""
Command Parser — ভয়েস থেকে সঠিক কাজ বোঝা
"""

import re
import datetime
from typing import Tuple


class CommandParser:
    def __init__(self, config, phone_controller):
        self.config = config
        self.phone = phone_controller

    def parse(self, text: str) -> Tuple[bool, str]:
        """
        Text parse করো এবং কাজ করো।
        Returns: (handled: bool, response: str)
        """
        t = text.lower().strip()

        # ── LOCAL / PC COMMANDS ───────────────────────────────────────────────
        result = self._local_commands(t)
        if result[0]:
            return result

        # ── PHONE COMMANDS ────────────────────────────────────────────────────
        if self.phone.is_connected():
            result = self._phone_commands(t)
            if result[0]:
                return result

        return False, ""

    # ══════════════════════════════════════════════════════════════════════════
    #  LOCAL / PC COMMANDS
    # ══════════════════════════════════════════════════════════════════════════

    def _local_commands(self, t: str) -> Tuple[bool, str]:

        # সময়
        if any(w in t for w in ["সময়", "time", "কটা বাজে", "কয়টা বাজে"]):
            now = datetime.datetime.now()
            return True, f"এখন সময় {now.strftime('%I:%M %p')}"

        # তারিখ
        if any(w in t for w in ["তারিখ", "date", "আজকে কত", "কত তারিখ"]):
            today = datetime.datetime.now()
            return True, f"আজকের তারিখ {today.strftime('%d %B, %Y')}"

        # Hello
        if any(w in t for w in ["হ্যালো", "hello", "hi", "আসসালামু", "নমস্কার"]):
            return True, f"হ্যালো! আমি {self.config.assistant_name}। কীভাবে সাহায্য করতে পারি?"

        # Help
        if any(w in t for w in ["help", "সাহায্য", "কী করতে পারো", "কমান্ড"]):
            return True, (
                "আমি এগুলো করতে পারি: "
                "Call করা, SMS পাঠানো, WhatsApp message, "
                "App খোলা, Music control, Screenshot নেওয়া, "
                "Volume control, WiFi/Bluetooth on-off, "
                "Battery দেখা, Torch জ্বালানো এবং আরো অনেক কিছু।"
            )

        # History clear
        if any(w in t for w in ["ইতিহাস মুছো", "conversation clear", "রিসেট"]):
            return True, "CLEAR_HISTORY"

        return False, ""

    # ══════════════════════════════════════════════════════════════════════════
    #  PHONE COMMANDS
    # ══════════════════════════════════════════════════════════════════════════

    def _phone_commands(self, t: str) -> Tuple[bool, str]:

        # ── CALL ──────────────────────────────────────────────────────────────
        if any(w in t for w in ["কল করো", "call করো", "ফোন করো", "ring করো", "dial করো"]):
            number = re.search(r"[\d]{6,}", t)
            if number:
                return True, self.phone.call(number.group())
            return True, "কোন নম্বরে call করব? নম্বরটা বলুন।"

        if any(w in t for w in ["call শেষ", "কল রাখো", "ফোন রাখো"]):
            return True, self.phone.end_call()

        # ── SMS ───────────────────────────────────────────────────────────────
        if any(w in t for w in ["sms পাঠাও", "মেসেজ পাঠাও", "text করো"]):
            number = re.search(r"[\d]{6,}", t)
            # নম্বরের পরের text হলো message
            if number:
                msg_start = t.find(number.group()) + len(number.group())
                message = t[msg_start:].strip()
                if not message:
                    message = "Jarvis থেকে message"
                return True, self.phone.send_sms(number.group(), message)
            return True, "কোন নম্বরে SMS পাঠাব? নম্বর বলুন।"

        # ── WHATSAPP ──────────────────────────────────────────────────────────
        if any(w in t for w in ["whatsapp", "হোয়াটসঅ্যাপ"]):
            if any(w in t for w in ["message পাঠাও", "text করো", "লিখো"]):
                number = re.search(r"[\d]{6,}", t)
                if number:
                    num_end = t.find(number.group()) + len(number.group())
                    message = t[num_end:].strip()
                    if not message:
                        message = "Jarvis থেকে message"
                    return True, self.phone.whatsapp_message(number.group(), message)
            return True, self.phone.open_app("whatsapp")

        # ── SCREENSHOT ────────────────────────────────────────────────────────
        if any(w in t for w in ["স্ক্রিনশট", "screenshot", "স্ক্রিন capture"]):
            return True, self.phone.take_screenshot()

        # ── SCREEN RECORD ─────────────────────────────────────────────────────
        if any(w in t for w in ["রেকর্ড করো", "screen record", "ভিডিও করো"]):
            duration_match = re.search(r"(\d+)\s*সেকেন্ড", t)
            duration = int(duration_match.group(1)) if duration_match else 10
            return True, self.phone.screen_record(duration)

        # ── VOLUME ────────────────────────────────────────────────────────────
        if any(w in t for w in ["ভলিউম", "volume", "শব্দ"]):
            if any(w in t for w in ["বাড়াও", "বাড়া", "up", "বেশি"]):
                return True, self.phone.volume_up()
            elif any(w in t for w in ["কমাও", "কমা", "down", "কম"]):
                return True, self.phone.volume_down()
            elif any(w in t for w in ["মিউট", "mute", "নিঃশব্দ"]):
                return True, self.phone.volume_mute()
            # Specific level: "ভলিউম ৫ করো"
            level_match = re.search(r"(\d+)", t)
            if level_match:
                return True, self.phone.set_volume(int(level_match.group(1)))

        # ── MUSIC / MEDIA ─────────────────────────────────────────────────────
        if any(w in t for w in ["pause", "পজ", "থামাও"]):
            return True, self.phone.media_play_pause()

        if any(w in t for w in ["play", "চালাও", "resume"]) and any(
            w in t for w in ["গান", "music", "মিউজিক", "song"]
        ):
            return True, self.phone.media_play_pause()

        if any(w in t for w in ["next", "পরের গান", "next song"]):
            return True, self.phone.media_next()

        if any(w in t for w in ["previous", "আগের গান", "back song"]):
            return True, self.phone.media_previous()

        if any(w in t for w in ["গান বন্ধ", "music stop", "stop song"]):
            return True, self.phone.media_stop()

        # YouTube search
        if "youtube" in t and any(w in t for w in ["চালাও", "play", "search", "দেখাও"]):
            query = re.sub(r"youtube.*?(চালাও|play|search|দেখাও)", "", t).strip()
            query = re.sub(r"(youtube|তে|এ)", "", query).strip()
            if query:
                return True, self.phone.play_youtube(query)
            return True, self.phone.open_app("youtube")

        # Spotify
        if "spotify" in t:
            query = re.sub(r"spotify.*?(চালাও|play|search)", "", t).strip()
            if query:
                return True, self.phone.play_spotify(query)
            return True, self.phone.play_spotify()

        # ── SCREEN ────────────────────────────────────────────────────────────
        if any(w in t for w in ["ফোন লক", "স্ক্রিন বন্ধ", "lock phone", "screen off"]):
            return True, self.phone.screen_off()

        if any(w in t for w in ["আনলক", "unlock", "স্ক্রিন চালু", "screen on", "ফোন খোলো"]):
            return True, self.phone.screen_on()

        # Brightness
        if any(w in t for w in ["brightness", "উজ্জ্বলতা"]):
            level_match = re.search(r"(\d+)", t)
            if level_match:
                pct = int(level_match.group(1))
                level = int(pct * 255 / 100)
                return True, self.phone.set_brightness(level)

        # ── CONNECTIVITY ──────────────────────────────────────────────────────
        if any(w in t for w in ["wifi", "ওয়াইফাই"]):
            if any(w in t for w in ["চালু", "on", "চালাও"]):
                return True, self.phone.wifi_on()
            elif any(w in t for w in ["বন্ধ", "off"]):
                return True, self.phone.wifi_off()
            return True, self.phone.get_wifi_info()

        if any(w in t for w in ["bluetooth", "ব্লুটুথ"]):
            if any(w in t for w in ["চালু", "on"]):
                return True, self.phone.bluetooth_on()
            elif any(w in t for w in ["বন্ধ", "off"]):
                return True, self.phone.bluetooth_off()

        if any(w in t for w in ["mobile data", "মোবাইল ডেটা", "ডেটা"]):
            if any(w in t for w in ["চালু", "on"]):
                return True, self.phone.mobile_data_on()
            elif any(w in t for w in ["বন্ধ", "off"]):
                return True, self.phone.mobile_data_off()

        if any(w in t for w in ["airplane mode", "ফ্লাইট মোড"]):
            if any(w in t for w in ["চালু", "on"]):
                return True, self.phone.airplane_mode_on()
            elif any(w in t for w in ["বন্ধ", "off"]):
                return True, self.phone.airplane_mode_off()

        # ── TORCH ─────────────────────────────────────────────────────────────
        if any(w in t for w in ["টর্চ", "torch", "flashlight", "আলো জ্বালাও"]):
            if any(w in t for w in ["চালু", "on", "জ্বালাও"]):
                return True, self.phone.torch_on()
            elif any(w in t for w in ["বন্ধ", "off"]):
                return True, self.phone.torch_off()

        # ── CAMERA ────────────────────────────────────────────────────────────
        if any(w in t for w in ["camera", "ক্যামেরা"]):
            if any(w in t for w in ["সামনের", "front", "selfie"]):
                return True, self.phone.open_front_camera()
            return True, self.phone.open_camera()

        # ── BATTERY ───────────────────────────────────────────────────────────
        if any(w in t for w in ["battery", "ব্যাটারি", "চার্জ কত"]):
            return True, self.phone.get_battery()

        # ── STORAGE ───────────────────────────────────────────────────────────
        if any(w in t for w in ["storage", "স্টোরেজ", "জায়গা কত"]):
            return True, self.phone.get_storage()

        # ── SILENT/RING ───────────────────────────────────────────────────────
        if any(w in t for w in ["silent", "নিঃশব্দ", "চুপ"]):
            return True, self.phone.set_ringer_silent()

        if any(w in t for w in ["ring চালু", "ringer on", "শব্দ চালু"]):
            return True, self.phone.set_ringer_normal()

        # ── NOTIFICATION ──────────────────────────────────────────────────────
        if any(w in t for w in ["notification", "নোটিফিকেশন"]):
            return True, self.phone.get_notifications()

        # ── NAVIGATION ────────────────────────────────────────────────────────
        if any(w in t for w in ["home button", "হোম বোতাম"]):
            return True, self.phone.press_home()

        if any(w in t for w in ["back", "ব্যাক", "পিছনে"]):
            return True, self.phone.press_back()

        if any(w in t for w in ["recent apps", "সাম্প্রতিক"]):
            return True, self.phone.press_recent_apps()

        # ── SEARCH ────────────────────────────────────────────────────────────
        if any(w in t for w in ["google করো", "search করো", "গুগল করো"]):
            query = re.sub(r"(google|search|গুগল)\s*(করো)?", "", t).strip()
            if query:
                return True, self.phone.search_google(query)

        # Maps
        if any(w in t for w in ["maps", "navigate", "যাওয়ার রাস্তা"]):
            location = re.sub(r"(maps|navigate|যাওয়ার|রাস্তা|দেখাও)", "", t).strip()
            if location:
                return True, self.phone.open_maps(location)

        # URL open
        if any(w in t for w in ["open", "খোলো"]) and "." in t:
            url_match = re.search(r"[\w-]+\.\w{2,}", t)
            if url_match:
                return True, self.phone.open_url(url_match.group())

        # ── APP OPEN ──────────────────────────────────────────────────────────
        if any(w in t for w in ["খোলো", "open", "চালাও", "চালু করো", "start"]):
            return True, self.phone.open_app(t)

        if any(w in t for w in ["বন্ধ করো", "close", "stop"]):
            return True, self.phone.close_app(t)

        return False, ""
