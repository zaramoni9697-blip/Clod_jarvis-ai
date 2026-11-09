"""
JARVIS - AI Voice Assistant with Android Phone Control
=======================================================
Requirements:
    pip install speechrecognition pyttsx3 openai pyaudio

Phone Setup:
    1. Settings → About Phone → Build Number (৭ বার tap করুন)
    2. Settings → Developer Options → USB Debugging চালু করুন
    3. USB দিয়ে PC-তে connect করুন
    4. ADB install করুন: https://developer.android.com/tools/adb

API Key:
    নিচের API_KEY-এ আপনার OpenAI key বসান
"""

import speech_recognition as sr
import pyttsx3
import openai
import os
import datetime
import subprocess
import re
import sys
import time

# ─── CONFIG ──────────────────────────────────────────────────────────────────
API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
ASSISTANT_NAME = "Jarvis"
VOICE_RATE = 160

# ADB path — Windows-এ সাধারণত এখানে থাকে
# Mac/Linux-এ শুধু "adb" লিখলেই হবে
ADB_PATH = "adb"  # পথ দিতে হলে: r"C:\platform-tools\adb.exe"

SYSTEM_PROMPT = """তুমি Jarvis, একজন AI assistant যে PC এবং Android phone দুটোই control করতে পারো।
উত্তর সংক্ষিপ্ত রাখো। বাংলা ও ইংরেজি দুটোতেই কথা বলতে পারো।"""
# ─────────────────────────────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════════════
#  ADB — PHONE CONTROL
# ══════════════════════════════════════════════════════════════════════════════

def adb(command):
    """ADB command run করো এবং output return করো"""
    try:
        result = subprocess.run(
            f"{ADB_PATH} {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip(), result.returncode == 0
    except subprocess.TimeoutExpired:
        return "timeout", False
    except FileNotFoundError:
        return "ADB পাওয়া যায়নি", False


def check_phone_connected():
    """Phone connected আছে কিনা চেক করো"""
    output, _ = adb("devices")
    lines = output.strip().split("\n")
    # "List of devices attached" বাদে আর কিছু থাকলে device connected
    devices = [l for l in lines[1:] if l.strip() and "device" in l]
    return len(devices) > 0


def phone_call(number):
    """Phone call করো"""
    # নম্বর থেকে শুধু digits নাও
    clean_number = re.sub(r"[^\d+]", "", number)
    output, success = adb(f'shell am start -a android.intent.action.CALL -d tel:{clean_number}')
    return success


def phone_sms(number, message):
    """SMS পাঠাও"""
    clean_number = re.sub(r"[^\d+]", "", number)
    # SMS app খুলে pre-fill করো
    output, success = adb(
        f'shell am start -a android.intent.action.SENDTO '
        f'-d sms:{clean_number} --es sms_body "{message}"'
    )
    return success


def open_app(app_name):
    """App খোলো — নাম দিয়ে package খুঁজে নেবে"""
    app_packages = {
        # Social Media
        "whatsapp": "com.whatsapp",
        "facebook": "com.facebook.katana",
        "instagram": "com.instagram.android",
        "youtube": "com.google.android.youtube",
        "tiktok": "com.zhiliaoapp.musically",
        "twitter": "com.twitter.android",
        "telegram": "org.telegram.messenger",
        # Google Apps
        "gmail": "com.google.android.gm",
        "maps": "com.google.android.apps.maps",
        "chrome": "com.android.chrome",
        "camera": "com.android.camera2",
        "photos": "com.google.android.apps.photos",
        "drive": "com.google.android.apps.docs",
        "meet": "com.google.android.apps.meetings",
        # System
        "settings": "com.android.settings",
        "phone": "com.android.dialer",
        "contacts": "com.android.contacts",
        "messages": "com.android.mms",
        "calculator": "com.android.calculator2",
        "clock": "com.android.deskclock",
        "music": "com.android.music",
        "spotify": "com.spotify.music",
        "files": "com.android.documentsui",
        "play store": "com.android.vending",
    }

    for key, package in app_packages.items():
        if key in app_name.lower():
            output, success = adb(
                f'shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
            )
            return success, key

    return False, app_name


def phone_volume(action):
    """Volume control — বাড়াও/কমাও/মিউট"""
    if action in ["বাড়াও", "up", "বাড়া"]:
        adb("shell input keyevent KEYCODE_VOLUME_UP")
        adb("shell input keyevent KEYCODE_VOLUME_UP")
        adb("shell input keyevent KEYCODE_VOLUME_UP")
        return "ভলিউম বাড়ানো হয়েছে"
    elif action in ["কমাও", "down", "কমা"]:
        adb("shell input keyevent KEYCODE_VOLUME_DOWN")
        adb("shell input keyevent KEYCODE_VOLUME_DOWN")
        adb("shell input keyevent KEYCODE_VOLUME_DOWN")
        return "ভলিউম কমানো হয়েছে"
    elif action in ["মিউট", "mute", "বন্ধ"]:
        adb("shell input keyevent KEYCODE_VOLUME_MUTE")
        return "মিউট করা হয়েছে"
    return "বুঝতে পারিনি"


def phone_screenshot():
    """Screenshot নাও এবং PC-তে save করো"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"

    # Phone-এ screenshot নাও
    adb(f"shell screencap -p /sdcard/{filename}")
    time.sleep(0.5)

    # PC-তে copy করো
    output, success = adb(f"pull /sdcard/{filename} ./{filename}")

    # Phone থেকে মুছে ফেলো
    adb(f"shell rm /sdcard/{filename}")

    if success:
        return f"Screenshot নেওয়া হয়েছে: {filename}"
    return "Screenshot নিতে পারিনি"


def phone_lock():
    """Phone lock/screen off করো"""
    adb("shell input keyevent KEYCODE_POWER")
    return "Phone lock করা হয়েছে"


def phone_unlock():
    """Phone unlock/wake করো"""
    adb("shell input keyevent KEYCODE_WAKEUP")
    time.sleep(0.3)
    adb("shell input keyevent KEYCODE_MENU")
    return "Phone unlock হয়েছে"


def phone_battery():
    """Battery status দেখো"""
    output, _ = adb("shell dumpsys battery | grep level")
    if output:
        level = re.search(r"level:\s*(\d+)", output)
        if level:
            return f"Battery {level.group(1)}% আছে"
    return "Battery তথ্য পাওয়া যায়নি"


def phone_wifi(action):
    """WiFi on/off করো"""
    if action in ["চালু", "on", "চালাও"]:
        adb("shell svc wifi enable")
        return "WiFi চালু করা হয়েছে"
    else:
        adb("shell svc wifi disable")
        return "WiFi বন্ধ করা হয়েছে"


def phone_bluetooth(action):
    """Bluetooth on/off করো"""
    if action in ["চালু", "on", "চালাও"]:
        adb("shell svc bluetooth enable")
        return "Bluetooth চালু করা হয়েছে"
    else:
        adb("shell svc bluetooth disable")
        return "Bluetooth বন্ধ করা হয়েছে"


def phone_torch(action):
    """Flashlight/torch on/off করো"""
    if action in ["চালু", "on", "জ্বালাও"]:
        adb("shell cmd flashlight on")
        return "Torch জ্বালানো হয়েছে"
    else:
        adb("shell cmd flashlight off")
        return "Torch বন্ধ করা হয়েছে"


def phone_type_text(text):
    """Phone-এ text type করো"""
    # Space replace করো (ADB-র জন্য)
    formatted = text.replace(" ", "%s")
    adb(f'shell input text "{formatted}"')
    return f"লেখা হয়েছে: {text}"


def phone_back():
    """Back button press করো"""
    adb("shell input keyevent KEYCODE_BACK")
    return "Back করা হয়েছে"


def phone_home():
    """Home button press করো"""
    adb("shell input keyevent KEYCODE_HOME")
    return "Home-এ গেছে"


def phone_notifications():
    """Notification panel নামাও"""
    adb("shell cmd statusbar expand-notifications")
    return "Notification panel খোলা হয়েছে"


# ══════════════════════════════════════════════════════════════════════════════
#  COMMAND PARSER — ভয়েস থেকে কাজ বোঝা
# ══════════════════════════════════════════════════════════════════════════════

def handle_phone_commands(text):
    """
    Phone-সম্পর্কিত commands handle করো
    Returns: (handled: bool, response: str)
    """

    # ── CALL ──────────────────────────────────────────────────────────────
    if any(w in text for w in ["কল করো", "call করো", "ফোন করো", "ring করো"]):
        # নম্বর বের করো
        number = re.search(r"[\d]{6,}", text)
        if number:
            success = phone_call(number.group())
            return True, f"{'কল করা হচ্ছে' if success else 'কল করতে পারিনি'} {number.group()}"
        return True, "কোন নম্বরে কল করব? নম্বর বলুন।"

    # ── SCREENSHOT ────────────────────────────────────────────────────────
    if any(w in text for w in ["স্ক্রিনশট", "screenshot"]):
        result = phone_screenshot()
        return True, result

    # ── VOLUME ────────────────────────────────────────────────────────────
    if any(w in text for w in ["ভলিউম", "volume", "শব্দ"]):
        if any(w in text for w in ["বাড়াও", "বাড়া", "up"]):
            return True, phone_volume("বাড়াও")
        elif any(w in text for w in ["কমাও", "কমা", "down"]):
            return True, phone_volume("কমাও")
        elif any(w in text for w in ["মিউট", "mute"]):
            return True, phone_volume("মিউট")

    # ── LOCK/UNLOCK ───────────────────────────────────────────────────────
    if any(w in text for w in ["ফোন লক", "স্ক্রিন বন্ধ", "lock phone"]):
        return True, phone_lock()

    if any(w in text for w in ["ফোন খোলো", "আনলক", "unlock", "স্ক্রিন চালু"]):
        return True, phone_unlock()

    # ── BATTERY ───────────────────────────────────────────────────────────
    if any(w in text for w in ["ব্যাটারি", "battery", "চার্জ কত"]):
        return True, phone_battery()

    # ── WIFI ──────────────────────────────────────────────────────────────
    if "wifi" in text or "ওয়াইফাই" in text:
        if any(w in text for w in ["চালু", "on", "চালাও"]):
            return True, phone_wifi("on")
        elif any(w in text for w in ["বন্ধ", "off"]):
            return True, phone_wifi("off")

    # ── BLUETOOTH ─────────────────────────────────────────────────────────
    if "bluetooth" in text or "ব্লুটুথ" in text:
        if any(w in text for w in ["চালু", "on"]):
            return True, phone_bluetooth("on")
        elif any(w in text for w in ["বন্ধ", "off"]):
            return True, phone_bluetooth("off")

    # ── TORCH ─────────────────────────────────────────────────────────────
    if any(w in text for w in ["টর্চ", "torch", "flashlight", "আলো"]):
        if any(w in text for w in ["চালু", "on", "জ্বালাও"]):
            return True, phone_torch("on")
        elif any(w in text for w in ["বন্ধ", "off"]):
            return True, phone_torch("off")

    # ── APP OPEN ──────────────────────────────────────────────────────────
    if any(w in text for w in ["খোলো", "open", "চালাও", "চালু করো"]):
        success, app = open_app(text)
        if success:
            return True, f"{app} খোলা হয়েছে"
        # App পাওয়া না গেলে AI-কে handle করতে দাও

    # ── NAVIGATION ────────────────────────────────────────────────────────
    if any(w in text for w in ["হোম", "home button"]):
        return True, phone_home()

    if any(w in text for w in ["ব্যাক", "back", "পিছনে যাও"]):
        return True, phone_back()

    if any(w in text for w in ["নোটিফিকেশন", "notification"]):
        return True, phone_notifications()

    return False, ""


def handle_local_commands(text):
    """PC-র local commands"""

    if any(w in text for w in ["সময়", "time", "কটা বাজে"]):
        now = datetime.datetime.now()
        return True, f"এখন সময় {now.strftime('%I:%M %p')}"

    if any(w in text for w in ["তারিখ", "date", "কত তারিখ"]):
        return True, f"আজকের তারিখ {datetime.datetime.now().strftime('%d %B, %Y')}"

    if any(w in text for w in ["হ্যালো", "hello", "hi"]):
        return True, "হ্যালো! PC এবং phone দুটোই control করতে পারি।"

    return False, ""


# ══════════════════════════════════════════════════════════════════════════════
#  VOICE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def setup_tts():
    engine = pyttsx3.init()
    engine.setProperty("rate", VOICE_RATE)
    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[0].id)
    return engine


def speak(engine, text):
    print(f"\n🤖 {ASSISTANT_NAME}: {text}\n")
    engine.say(text)
    engine.runAndWait()


def listen(recognizer, microphone):
    print("🎤 শুনছি...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return None

    try:
        text = recognizer.recognize_google(audio, language="bn-BD")
        print(f"👤 আপনি: {text}")
        return text.lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"❌ Speech error: {e}")
        return None


def ask_ai(client, history, user_message):
    history.append({"role": "user", "content": user_message})
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
            max_tokens=150,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": reply})
        if len(history) > 20:
            history[:] = history[-20:]
        return reply
    except Exception as e:
        return f"সমস্যা হলো: {e}"


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print(f"   🤖 {ASSISTANT_NAME} — PC + Android Phone Controller")
    print("=" * 55)

    # API key check
    ai_enabled = API_KEY != "YOUR_OPENAI_API_KEY_HERE"
    if not ai_enabled:
        print("⚠️  OpenAI API key নেই — শুধু phone/local commands কাজ করবে\n")

    # Phone connection check
    phone_connected = check_phone_connected()
    if phone_connected:
        print("✅ Android phone connected!")
    else:
        print("⚠️  Phone connected নয়। USB debugging চালু করে connect করুন।")
        print("   Phone commands কাজ করবে না।\n")

    # Initialize
    tts_engine = setup_tts()
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    client = openai.OpenAI(api_key=API_KEY) if ai_enabled else None
    history = []

    speak(tts_engine, f"Jarvis চালু। {'Phone connected.' if phone_connected else 'Phone connect করুন।'}")

    print("\n💡 Commands:")
    print("   Phone: 'WhatsApp খোলো', 'ভলিউম বাড়াও', 'স্ক্রিনশট নাও'")
    print("   PC:    'সময় কত', 'তারিখ কত'")
    print("   AI:    যেকোনো প্রশ্ন")
    print("   বন্ধ:  'বিদায়' অথবা Ctrl+C\n")

    # ─── MAIN LOOP ─────────────────────────────────────────────────────────
    while True:
        try:
            user_input = listen(recognizer, microphone)
            if not user_input:
                continue

            # Exit
            if any(w in user_input for w in ["বিদায়", "bye", "exit", "বন্ধ করো"]):
                speak(tts_engine, "বিদায়! আবার ডাকলেই আসব।")
                break

            response = None

            # ১. Phone commands চেক করো
            if phone_connected:
                handled, response = handle_phone_commands(user_input)
                if handled:
                    speak(tts_engine, response)
                    continue

            # ২. Local commands চেক করো
            handled, response = handle_local_commands(user_input)
            if handled:
                speak(tts_engine, response)
                continue

            # ৩. AI-কে দাও
            if ai_enabled:
                print("🧠 ভাবছি...")
                response = ask_ai(client, history, user_input)
                speak(tts_engine, response)
            else:
                speak(tts_engine, "AI বন্ধ। API key দিলে সব প্রশ্নের উত্তর দেব।")

        except KeyboardInterrupt:
            print("\n👋 Jarvis বন্ধ হচ্ছে...")
            speak(tts_engine, "বিদায়!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
