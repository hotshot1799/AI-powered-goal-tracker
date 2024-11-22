from groq import Groq
from app.core.config import settings
from typing import Optional

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def analyze_progress(self, progress_text: str, goal_context: str) -> float:
        prompt = f"""
        Goal Context: {goal_context}
        Progress Update: {progress_text}
        Task: Calculate the percentage of progress towards this goal based on the update.
        Return only the numerical percentage between 0 and 100.
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )
            
            response_text = ""
            for chunk in completion:
                response_text += chunk.choices[0].delta.content or ""
            
            progress_value = float(response_text.strip())
            return max(0, min(100, progress_value))
        except Exception as e:
            print(f"AI analysis error: {str(e)}")
            return 0.0
