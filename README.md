# 🤖 Jarvis AI — Personal Voice Assistant

> PC + Android Phone Control করুন শুধু ভয়েস দিয়ে

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-green)
![Android](https://img.shields.io/badge/Android-5.0+-orange)

---

## ✨ Features

| Category | কী করতে পারে |
|----------|-------------|
| 📞 **Call & SMS** | Call করা, SMS ও WhatsApp message পাঠানো |
| 📱 **Apps** | যেকোনো app open/close করা |
| 🎵 **Music** | Play/Pause/Next/Previous, YouTube, Spotify |
| 📸 **Camera** | Screenshot, Screen Record, Camera খোলা |
| 🔊 **Volume** | বাড়ানো/কমানো/মিউট/Silent mode |
| 🌐 **Internet** | WiFi, Bluetooth, Mobile Data on/off |
| 🔦 **Torch** | Flashlight on/off |
| 🔋 **System** | Battery %, Storage info, Notifications |
| 🧠 **AI Chat** | যেকোনো প্রশ্নের উত্তর (OpenAI GPT) |
| 🗺️ **Search** | Google search, Maps navigation |

---

## 📋 Requirements

- Python 3.8+
- Android Phone (USB Debugging চালু)
- ADB (Android Debug Bridge)
- OpenAI API Key (optional, AI chat-এর জন্য)

---

## 🚀 Setup

### ১. Repository Clone করুন
```bash
git clone https://github.com/YOUR_USERNAME/jarvis-ai.git
cd jarvis-ai
```

### ২. Packages Install করুন
```bash
pip install -r requirements.txt
```

> **Windows-এ PyAudio সমস্যা হলে:**
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### ৩. ADB Install করুন
👉 [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools) download করুন

**Windows:** Extract করে `C:\platform-tools\` এ রাখুন, PATH-এ যোগ করুন।

**Mac:**
```bash
brew install android-platform-tools
```

**Linux:**
```bash
sudo apt install adb
```

### ৪. Phone Setup করুন
```
Settings → About Phone
→ Build Number (৭ বার tap করুন)
→ Developer Options চালু হবে
→ Developer Options → USB Debugging ✅
```
USB দিয়ে PC-তে connect করুন → Phone-এ "Allow" দিন।

**Test করুন:**
```bash
adb devices
# Output: List of devices attached
#         XXXXXXXX   device
```

### ৫. API Key দিন (Optional)
`jarvis/config.py` ফাইলে:
```python
openai_api_key: str = "YOUR_KEY_HERE"
```
অথবা environment variable:
```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Mac/Linux
export OPENAI_API_KEY=your-key-here
```
API Key পাবেন: [platform.openai.com](https://platform.openai.com/api-keys)

### ৬. Jarvis চালু করুন
```bash
python main.py
```

---

## 🎤 ভয়েস কমান্ড

### 📞 Call & Message
```
"01712345678 কল করো"
"01712345678 sms পাঠাও হ্যালো ভাই"
"01712345678 whatsapp message পাঠাও"
"কল রাখো"
```

### 📱 Apps
```
"WhatsApp খোলো"
"YouTube খোলো"
"Settings খোলো"
"bKash খোলো"
"Instagram বন্ধ করো"
```

### 🎵 Music
```
"গান চালাও"
"pause"
"next song"
"আগের গান"
"YouTube-এ রবীন্দ্রসংগীত চালাও"
"Spotify খোলো"
```

### 🔊 Volume & Sound
```
"ভলিউম বাড়াও"
"ভলিউম কমাও"
"মিউট করো"
"silent mode"
"ভলিউম ৮ করো"
```

### 📸 Screen
```
"স্ক্রিনশট নাও"
"screen record করো"
"ফোন লক করো"
"আনলক করো"
"brightness ৮০ করো"
```

### 🌐 Connectivity
```
"WiFi চালু"
"WiFi বন্ধ"
"Bluetooth চালু"
"Mobile data বন্ধ"
"Airplane mode চালু"
```

### 🔋 System Info
```
"battery কত"
"storage কত"
"সময় কত"
"তারিখ কত"
"notification দেখাও"
```

---

## 📁 Project Structure

```
jarvis-ai/
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
└── jarvis/
    ├── __init__.py
    ├── config.py           # সব settings
    ├── assistant.py        # Main controller
    ├── voice.py            # Speech recognition + TTS
    ├── ai_brain.py         # OpenAI integration
    ├── phone_controller.py # ADB phone control
    └── command_parser.py   # Voice → Action mapping
```

---

## ⚙️ Configuration

`jarvis/config.py` এ সব settings আছে:

```python
# AI Model পরিবর্তন
ai_model: str = "gpt-4"  # বা "gpt-3.5-turbo"

# Language পরিবর্তন
speech_language: str = "en-US"  # English এর জন্য

# Voice speed
tts_rate: int = 160  # 100-200

# Custom app packages যোগ করুন
app_packages: dict = {
    "my app": "com.myapp.package",
    ...
}
```

---

## 🔧 Troubleshooting

**PyAudio install error:**
```bash
# Windows
pip install pipwin && pipwin install pyaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# Mac
brew install portaudio
pip install pyaudio
```

**ADB not found:**
- Platform Tools download করুন
- PATH-এ add করুন
- PC restart দিন

**Phone not connecting:**
- USB cable বদলে দেখুন
- USB Debugging on আছে কিনা দেখুন
- Phone-এ "Allow" দিয়েছেন কিনা দেখুন
- `adb kill-server && adb start-server` চালান

**Speech not working:**
- Internet connection চেক করুন
- Microphone permission দিন

---

## 📄 License

MIT License — Free to use, modify and distribute.

---

## 🤝 Contributing

Pull request welcome! নতুন feature add করতে চাইলে:
1. Fork করুন
2. Feature branch বানান: `git checkout -b feature/new-feature`
3. Commit করুন: `git commit -m 'Add new feature'`
4. Push করুন: `git push origin feature/new-feature`
5. Pull Request খুলুন

---

*Built with ❤️ — Powered by OpenAI + Android ADB*
