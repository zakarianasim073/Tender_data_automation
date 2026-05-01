import os
from typing import Any, Dict, List


class GPTClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.client = None
        else:
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
            except ImportError:
                self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

    async def chat(self, user_id: str, messages: List[Dict[str, str]], language: str = "en"):
        if self.client is None:
            return {
                "success": False,
                "error": "OpenAI is not configured. Install openai and set OPENAI_API_KEY to use GPT chat.",
            }
        if language == "bn":
            messages.insert(0, {"role": "system", "content": "Respond in Bengali (বাংলা) using formal tender/BOQ terminology."})
        try:
            res = self.client.chat.completions.create(model=self.model, messages=messages, user=user_id)
            return {"success": True, "content": res.choices[0].message.content, "tokens_used": res.usage.total_tokens}
        except Exception as e:
            return {"success": False, "error": str(e)}
