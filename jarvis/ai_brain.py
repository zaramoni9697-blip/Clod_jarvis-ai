"""
AI Brain — OpenAI GPT Integration
"""

import openai
from typing import List, Dict


class AIBrain:
    def __init__(self, config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.openai_api_key) if config.ai_enabled else None
        self.history: List[Dict] = []

    def think(self, user_message: str) -> str:
        """AI-কে প্রশ্ন করো এবং উত্তর নাও"""
        if not self.config.ai_enabled:
            return "AI বন্ধ আছে। config.py-তে OpenAI API key দিন।"

        self.history.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.config.ai_model,
                messages=[
                    {"role": "system", "content": self.config.ai_system_prompt},
                    *self.history
                ],
                max_tokens=200,
                temperature=0.7
            )

            reply = response.choices[0].message.content.strip()
            self.history.append({"role": "assistant", "content": reply})

            # History বড় হলে পুরনো কাটো
            if len(self.history) > self.config.max_history:
                self.history = self.history[-self.config.max_history:]

            return reply

        except openai.AuthenticationError:
            return "API key সঠিক নয়। config.py চেক করুন।"
        except openai.RateLimitError:
            return "API limit শেষ। একটু পরে আবার চেষ্টা করুন।"
        except Exception as e:
            return f"AI error: {str(e)}"

    def clear_history(self):
        """Conversation history মুছে ফেলো"""
        self.history.clear()
