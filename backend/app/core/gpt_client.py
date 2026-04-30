import openai, os
from typing import List, Dict, Any

class GPTClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo"
    
    async def chat(self, user_id: str, messages: List[Dict[str, str]], language: str = "en"):
        if language == "bn":
            messages.insert(0, {"role": "system", "content": "Respond in Bengali (বাংলা) using formal tender/BOQ terminology."})
        try:
            res = self.client.chat.completions.create(model=self.model, messages=messages, user=user_id)
            return {"success": True, "content": res.choices[0].message.content, "tokens_used": res.usage.total_tokens}
        except Exception as e:
            return {"success": False, "error": str(e)}
