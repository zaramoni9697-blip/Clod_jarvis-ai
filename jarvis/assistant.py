"""
Jarvis Assistant — সব module একসাথে জোড়া দেয়
"""

from .voice import VoiceEngine
from .ai_brain import AIBrain
from .phone_controller import PhoneController
from .command_parser import CommandParser
from .config import Config


class JarvisAssistant:
    def __init__(self, config: Config):
        self.config = config

        print("🔧 Voice engine চালু হচ্ছে...")
        self.voice = VoiceEngine(config)

        print("🧠 AI brain চালু হচ্ছে...")
        self.ai = AIBrain(config)

        print("📱 Phone controller চালু হচ্ছে...")
        self.phone = PhoneController(config)

        print("🎯 Command parser চালু হচ্ছে...")
        self.parser = CommandParser(config, self.phone)

    def start(self):
        """Jarvis শুরু করো"""
        self._print_status()

        # Greeting
        if self.phone.is_connected():
            device = self.phone.get_device_info()
            self.voice.speak(
                f"Jarvis চালু। {device['model']} connected। আপনার সেবায় প্রস্তুত।"
            )
        else:
            self.voice.speak(
                f"Jarvis চালু। Phone connect করুন। আপনার সেবায় প্রস্তুত।"
            )

        self._print_commands()

        # Main loop
        while True:
            try:
                user_input = self.voice.listen()

                if not user_input:
                    continue

                # Exit check
                if any(w in user_input for w in ["বিদায়", "bye", "exit", "বন্ধ করো", "goodbye"]):
                    self.voice.speak("বিদায়! আবার ডাকলেই আসব।")
                    break

                # Command parse করো
                handled, response = self.parser.parse(user_input)

                if handled:
                    if response == "CLEAR_HISTORY":
                        self.ai.clear_history()
                        self.voice.speak("Conversation ইতিহাস মুছে ফেলা হয়েছে।")
                    else:
                        self.voice.speak(response)

                elif self.config.ai_enabled:
                    # AI-কে দাও
                    print("🧠 AI ভাবছে...")
                    ai_response = self.ai.think(user_input)
                    self.voice.speak(ai_response)

                else:
                    self.voice.speak(
                        "AI বন্ধ আছে। config.py-তে OpenAI API key দিন।"
                    )

            except KeyboardInterrupt:
                print("\n\n👋 Jarvis বন্ধ হচ্ছে...")
                self.voice.speak("বিদায়!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    def _print_status(self):
        """Status দেখাও"""
        print("\n" + "═" * 55)
        print(f"  ✅ AI:    {'চালু ✓' if self.config.ai_enabled else 'বন্ধ ✗ (API key দিন)'}")
        print(f"  ✅ Phone: {'Connected ✓' if self.phone.is_connected() else 'Not Connected ✗'}")
        print(f"  ✅ Voice: চালু ✓")
        print("═" * 55 + "\n")

    def _print_commands(self):
        """Available commands দেখাও"""
        print("💡 ভয়েস কমান্ড:")
        print("  📱 Phone  : 'WhatsApp খোলো', 'ভলিউম বাড়াও', 'স্ক্রিনশট নাও'")
        print("  📞 Call   : '01712345678 কল করো'")
        print("  💬 SMS    : '01712345678 sms পাঠাও হ্যালো'")
        print("  🎵 Music  : 'গান চালাও', 'next song', 'pause'")
        print("  🔋 Info   : 'battery কত', 'storage কত'")
        print("  🧠 AI     : যেকোনো প্রশ্ন করুন")
        print("  🚪 বন্ধ   : 'বিদায়' অথবা Ctrl+C")
        print()
