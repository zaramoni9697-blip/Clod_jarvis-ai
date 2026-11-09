"""
Android Phone Controller — ADB দিয়ে সব Phone Control
"""

import subprocess
import re
import time
import datetime
import os
from typing import Tuple, Optional


class PhoneController:
    def __init__(self, config):
        self.config = config
        self.adb = config.adb_path

    # ══════════════════════════════════════════════════════════════════════════
    #  CORE ADB
    # ══════════════════════════════════════════════════════════════════════════

    def _run(self, command: str) -> Tuple[str, bool]:
        """ADB command চালাও"""
        try:
            result = subprocess.run(
                f"{self.adb} {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.stdout.strip(), result.returncode == 0
        except subprocess.TimeoutExpired:
            return "timeout", False
        except FileNotFoundError:
            return "ADB পাওয়া যায়নি। Platform Tools install করুন।", False

    def is_connected(self) -> bool:
        """Phone connected আছে কিনা চেক করো"""
        output, _ = self._run("devices")
        lines = [l for l in output.split("\n")[1:] if l.strip() and "device" in l]
        return len(lines) > 0

    def get_device_info(self) -> dict:
        """Phone-এর তথ্য নাও"""
        model, _ = self._run("shell getprop ro.product.model")
        android, _ = self._run("shell getprop ro.build.version.release")
        return {"model": model, "android": android}

    # ══════════════════════════════════════════════════════════════════════════
    #  CALLS & SMS
    # ══════════════════════════════════════════════════════════════════════════

    def call(self, number: str) -> str:
        """Phone call করো"""
        clean = re.sub(r"[^\d+]", "", number)
        if not clean:
            return "নম্বর ঠিক নেই।"
        _, success = self._run(f'shell am start -a android.intent.action.CALL -d tel:{clean}')
        return f"{clean} নম্বরে call করা হচ্ছে" if success else "Call করতে পারিনি।"

    def end_call(self) -> str:
        """Call শেষ করো"""
        self._run("shell input keyevent KEYCODE_ENDCALL")
        return "Call শেষ করা হয়েছে।"

    def send_sms(self, number: str, message: str) -> str:
        """SMS পাঠাও"""
        clean = re.sub(r"[^\d+]", "", number)
        # SMS app খুলে pre-fill করো
        _, success = self._run(
            f'shell am start -a android.intent.action.SENDTO '
            f'-d sms:{clean} --es sms_body "{message}" --ez exit_on_sent true'
        )
        if success:
            time.sleep(1)
            # Send button press করো (coordinates vary — standard button)
            self._run("shell input keyevent KEYCODE_ENTER")
            return f"{clean}-এ SMS পাঠানো হয়েছে।"
        return "SMS পাঠাতে পারিনি।"

    def whatsapp_message(self, number: str, message: str) -> str:
        """WhatsApp message পাঠাও"""
        clean = re.sub(r"[^\d+]", "", number)
        # Country code যোগ করো (Bangladesh: +880)
        if not clean.startswith("+"):
            if clean.startswith("0"):
                clean = "+88" + clean
            else:
                clean = "+880" + clean

        import urllib.parse
        encoded_msg = urllib.parse.quote(message)
        _, success = self._run(
            f'shell am start -a android.intent.action.VIEW '
            f'-d "https://api.whatsapp.com/send?phone={clean}&text={encoded_msg}"'
        )
        return "WhatsApp message তৈরি হয়েছে। Send করুন।" if success else "WhatsApp খুলতে পারিনি।"

    # ══════════════════════════════════════════════════════════════════════════
    #  APPS
    # ══════════════════════════════════════════════════════════════════════════

    def open_app(self, app_name: str) -> str:
        """App খোলো"""
        app_lower = app_name.lower()

        for key, package in self.config.app_packages.items():
            if key in app_lower or app_lower in key:
                _, success = self._run(
                    f'shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
                )
                return f"{key} খোলা হয়েছে।" if success else f"{key} install নেই।"

        # Package name দিয়ে সরাসরি open
        _, success = self._run(
            f'shell monkey -p {app_lower} -c android.intent.category.LAUNCHER 1'
        )
        return f"App খোলার চেষ্টা করা হচ্ছে।" if success else f"'{app_name}' পাওয়া যায়নি।"

    def close_app(self, app_name: str) -> str:
        """App বন্ধ করো"""
        app_lower = app_name.lower()
        for key, package in self.config.app_packages.items():
            if key in app_lower:
                self._run(f'shell am force-stop {package}')
                return f"{key} বন্ধ করা হয়েছে।"
        return f"'{app_name}' বন্ধ করতে পারিনি।"

    def list_installed_apps(self) -> str:
        """Installed apps-এর list"""
        output, _ = self._run("shell pm list packages -3")  # Third-party only
        packages = [line.replace("package:", "") for line in output.split("\n") if line.strip()]
        return f"{len(packages)}টি app installed।"

    # ══════════════════════════════════════════════════════════════════════════
    #  MEDIA & MUSIC
    # ══════════════════════════════════════════════════════════════════════════

    def media_play_pause(self) -> str:
        """Play/Pause toggle"""
        self._run("shell input keyevent KEYCODE_MEDIA_PLAY_PAUSE")
        return "Play/Pause করা হয়েছে।"

    def media_next(self) -> str:
        """Next track"""
        self._run("shell input keyevent KEYCODE_MEDIA_NEXT")
        return "Next track।"

    def media_previous(self) -> str:
        """Previous track"""
        self._run("shell input keyevent KEYCODE_MEDIA_PREVIOUS")
        return "Previous track।"

    def media_stop(self) -> str:
        """Stop music"""
        self._run("shell input keyevent KEYCODE_MEDIA_STOP")
        return "Music বন্ধ করা হয়েছে।"

    def play_youtube(self, query: str) -> str:
        """YouTube-এ গান/video search করো"""
        import urllib.parse
        encoded = urllib.parse.quote(query)
        self._run(
            f'shell am start -a android.intent.action.VIEW '
            f'-d "https://www.youtube.com/results?search_query={encoded}" '
            f'com.google.android.youtube'
        )
        return f"YouTube-এ '{query}' search করা হয়েছে।"

    def play_spotify(self, query: str = "") -> str:
        """Spotify খোলো"""
        if query:
            import urllib.parse
            encoded = urllib.parse.quote(query)
            self._run(
                f'shell am start -a android.intent.action.VIEW '
                f'-d "spotify:search:{encoded}"'
            )
            return f"Spotify-তে '{query}' search করা হয়েছে।"
        else:
            return self.open_app("spotify")

    # ══════════════════════════════════════════════════════════════════════════
    #  VOLUME & SOUND
    # ══════════════════════════════════════════════════════════════════════════

    def volume_up(self, steps: int = 3) -> str:
        for _ in range(steps):
            self._run("shell input keyevent KEYCODE_VOLUME_UP")
        return f"Volume বাড়ানো হয়েছে।"

    def volume_down(self, steps: int = 3) -> str:
        for _ in range(steps):
            self._run("shell input keyevent KEYCODE_VOLUME_DOWN")
        return "Volume কমানো হয়েছে।"

    def volume_mute(self) -> str:
        self._run("shell input keyevent KEYCODE_VOLUME_MUTE")
        return "Mute করা হয়েছে।"

    def set_volume(self, level: int) -> str:
        """Volume specific level-এ set করো (0-15)"""
        level = max(0, min(15, level))
        self._run(f"shell media volume --stream 3 --set {level}")
        return f"Volume {level}-এ set করা হয়েছে।"

    def set_ringer_silent(self) -> str:
        """Silent mode চালু করো"""
        self._run("shell cmd media_session volume --stream 2 --set 0")
        return "Silent mode চালু।"

    def set_ringer_normal(self) -> str:
        """Normal ringer চালু করো"""
        self._run("shell cmd media_session volume --stream 2 --set 7")
        return "Normal ringer চালু।"

    # ══════════════════════════════════════════════════════════════════════════
    #  SCREEN & POWER
    # ══════════════════════════════════════════════════════════════════════════

    def screen_off(self) -> str:
        """Screen বন্ধ করো"""
        self._run("shell input keyevent KEYCODE_POWER")
        return "Screen বন্ধ।"

    def screen_on(self) -> str:
        """Screen চালু করো"""
        self._run("shell input keyevent KEYCODE_WAKEUP")
        time.sleep(0.3)
        self._run("shell input swipe 540 1500 540 500")  # Swipe up to unlock
        return "Screen চালু।"

    def take_screenshot(self, save_path: str = ".") -> str:
        """Screenshot নাও"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        remote = f"/sdcard/{filename}"
        local = os.path.join(save_path, filename)

        self._run(f"shell screencap -p {remote}")
        time.sleep(0.5)
        _, success = self._run(f"pull {remote} {local}")
        self._run(f"shell rm {remote}")

        return f"Screenshot saved: {filename}" if success else "Screenshot নিতে পারিনি।"

    def screen_record(self, duration: int = 10) -> str:
        """Screen record করো"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        remote = f"/sdcard/record_{timestamp}.mp4"
        self._run(f"shell screenrecord --time-limit {duration} {remote} &")
        return f"{duration} সেকেন্ড record হচ্ছে।"

    def set_brightness(self, level: int) -> str:
        """Brightness set করো (0-255)"""
        level = max(0, min(255, level))
        self._run("shell settings put system screen_brightness_mode 0")  # Manual mode
        self._run(f"shell settings put system screen_brightness {level}")
        return f"Brightness {int(level/255*100)}% করা হয়েছে।"

    # ══════════════════════════════════════════════════════════════════════════
    #  CONNECTIVITY
    # ══════════════════════════════════════════════════════════════════════════

    def wifi_on(self) -> str:
        self._run("shell svc wifi enable")
        return "WiFi চালু।"

    def wifi_off(self) -> str:
        self._run("shell svc wifi disable")
        return "WiFi বন্ধ।"

    def bluetooth_on(self) -> str:
        self._run("shell svc bluetooth enable")
        return "Bluetooth চালু।"

    def bluetooth_off(self) -> str:
        self._run("shell svc bluetooth disable")
        return "Bluetooth বন্ধ।"

    def mobile_data_on(self) -> str:
        self._run("shell svc data enable")
        return "Mobile data চালু।"

    def mobile_data_off(self) -> str:
        self._run("shell svc data disable")
        return "Mobile data বন্ধ।"

    def airplane_mode_on(self) -> str:
        self._run("shell settings put global airplane_mode_on 1")
        self._run("shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true")
        return "Airplane mode চালু।"

    def airplane_mode_off(self) -> str:
        self._run("shell settings put global airplane_mode_on 0")
        self._run("shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false")
        return "Airplane mode বন্ধ।"

    def get_wifi_info(self) -> str:
        """Connected WiFi-এর তথ্য"""
        output, _ = self._run("shell dumpsys wifi | grep 'mWifiInfo'")
        ssid_match = re.search(r'SSID: ([^,]+)', output)
        return f"WiFi: {ssid_match.group(1)}" if ssid_match else "WiFi তথ্য পাওয়া যায়নি।"

    # ══════════════════════════════════════════════════════════════════════════
    #  SYSTEM INFO
    # ══════════════════════════════════════════════════════════════════════════

    def get_battery(self) -> str:
        """Battery percentage"""
        output, _ = self._run("shell dumpsys battery")
        level = re.search(r"level:\s*(\d+)", output)
        status = re.search(r"status:\s*(\d+)", output)

        if level:
            pct = level.group(1)
            charging = status and status.group(1) == "2"
            charge_status = "⚡ চার্জ হচ্ছে" if charging else "🔋"
            return f"Battery {pct}% {charge_status}"
        return "Battery তথ্য পাওয়া যায়নি।"

    def get_storage(self) -> str:
        """Storage info"""
        output, _ = self._run("shell df /sdcard")
        lines = output.split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 4:
                total = int(parts[1]) // 1024
                used = int(parts[2]) // 1024
                free = int(parts[3]) // 1024
                return f"Storage: Total {total}MB, Used {used}MB, Free {free}MB"
        return "Storage তথ্য পাওয়া যায়নি।"

    def get_notifications(self) -> str:
        """Notification panel নামাও"""
        self._run("shell cmd statusbar expand-notifications")
        return "Notification panel খোলা হয়েছে।"

    # ══════════════════════════════════════════════════════════════════════════
    #  TORCH & CAMERA
    # ══════════════════════════════════════════════════════════════════════════

    def torch_on(self) -> str:
        self._run("shell cmd flashlight on")
        return "Torch জ্বালানো হয়েছে।"

    def torch_off(self) -> str:
        self._run("shell cmd flashlight off")
        return "Torch বন্ধ।"

    def open_camera(self) -> str:
        self._run("shell am start -a android.media.action.IMAGE_CAPTURE")
        return "Camera খোলা হয়েছে।"

    def open_front_camera(self) -> str:
        self._run(
            'shell am start -a android.media.action.IMAGE_CAPTURE '
            '--ei android.intent.extras.CAMERA_FACING 1'
        )
        return "Front camera খোলা হয়েছে।"

    # ══════════════════════════════════════════════════════════════════════════
    #  NAVIGATION
    # ══════════════════════════════════════════════════════════════════════════

    def press_home(self) -> str:
        self._run("shell input keyevent KEYCODE_HOME")
        return "Home।"

    def press_back(self) -> str:
        self._run("shell input keyevent KEYCODE_BACK")
        return "Back।"

    def press_recent_apps(self) -> str:
        self._run("shell input keyevent KEYCODE_APP_SWITCH")
        return "Recent apps।"

    def swipe_up(self) -> str:
        self._run("shell input swipe 540 1500 540 500 300")
        return "Swipe up।"

    def swipe_down(self) -> str:
        self._run("shell input swipe 540 500 540 1500 300")
        return "Swipe down।"

    def type_text(self, text: str) -> str:
        """Phone-এ text type করো"""
        formatted = text.replace(" ", "%s").replace("'", "\\'")
        self._run(f'shell input text "{formatted}"')
        return f"Text type করা হয়েছে।"

    def open_url(self, url: str) -> str:
        """Browser-এ URL খোলো"""
        if not url.startswith("http"):
            url = "https://" + url
        self._run(f'shell am start -a android.intent.action.VIEW -d "{url}"')
        return f"{url} খোলা হয়েছে।"

    def search_google(self, query: str) -> str:
        """Google-এ search করো"""
        import urllib.parse
        encoded = urllib.parse.quote(query)
        self._run(
            f'shell am start -a android.intent.action.VIEW '
            f'-d "https://www.google.com/search?q={encoded}"'
        )
        return f"Google-এ '{query}' search করা হয়েছে।"

    def open_maps(self, location: str) -> str:
        """Google Maps-এ location খোলো"""
        import urllib.parse
        encoded = urllib.parse.quote(location)
        self._run(
            f'shell am start -a android.intent.action.VIEW '
            f'-d "geo:0,0?q={encoded}"'
        )
        return f"Maps-এ '{location}' খোলা হয়েছে।"

    # ══════════════════════════════════════════════════════════════════════════
    #  FILES
    # ══════════════════════════════════════════════════════════════════════════

    def push_file(self, local_path: str, remote_path: str = "/sdcard/") -> str:
        """PC থেকে Phone-এ file পাঠাও"""
        _, success = self._run(f'push "{local_path}" "{remote_path}"')
        filename = os.path.basename(local_path)
        return f"{filename} phone-এ পাঠানো হয়েছে।" if success else "File পাঠাতে পারিনি।"

    def pull_file(self, remote_path: str, local_path: str = ".") -> str:
        """Phone থেকে PC-তে file নাও"""
        _, success = self._run(f'pull "{remote_path}" "{local_path}"')
        return "File PC-তে নেওয়া হয়েছে।" if success else "File নিতে পারিনি।"
