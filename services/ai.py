from groq import Groq
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def analyze_data(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )
            
            response_text = ""
            for chunk in completion:
                response_text += chunk.choices[0].delta.content or ""
            
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            raise
