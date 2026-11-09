"""
╔══════════════════════════════════════════════════════════╗
║          JARVIS AI — Personal Voice Assistant            ║
║          PC + Android Phone Control                      ║
╚══════════════════════════════════════════════════════════╝

Author  : Your Name
GitHub  : https://github.com/YOUR_USERNAME/jarvis-ai
Version : 2.0.0
"""

import sys
import os

# Project root-কে path-এ যোগ করো
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis.assistant import JarvisAssistant
from jarvis.config import Config


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║          JARVIS AI v2.0 — Starting Up...                 ║
╚══════════════════════════════════════════════════════════╝
    """)

    config = Config()
    assistant = JarvisAssistant(config)
    assistant.start()


if __name__ == "__main__":
    main()
