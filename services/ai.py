from groq import Groq
from core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama3-8b-8192"  # Default model

    async def analyze_data(self, prompt: str) -> str:
        try:
            completion = await self.client.chat.completions.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            raise

    async def analyze_progress(self, goal_description: str, update_text: str) -> dict:
        prompt = f"""
        Goal: {goal_description}
        Progress Update: {update_text}

        Based on this progress update:
        1. Calculate a completion percentage (0-100)
        2. Provide a brief analysis of the progress

        Return only a JSON object with the following format:
        {{
            "percentage": number,
            "analysis": "brief explanation"
        }}
        """

        try:
            response = await self.analyze_data(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Progress analysis error: {str(e)}")
            return {
                "percentage": 0,
                "analysis": "Unable to analyze progress at this time."
            }

    async def get_suggestions(self, goals: list) -> list:
        goals_text = "\n".join([
            f"Goal {i+1}: {goal['description']} (Category: {goal['category']})"
            for i, goal in enumerate(goals)
        ])

        prompt = f"""
        Based on these goals:
        {goals_text}

        Provide exactly 3 specific, actionable suggestions that will help achieve these goals.
        Each suggestion should be practical and directly related to the goals.
        Format your response as a simple list with each suggestion on a new line.
        Do not number the suggestions or add any extra formatting.
        """

        try:
            response = await self.analyze_data(prompt)
            suggestions = [s.strip() for s in response.split('\n') if s.strip()]
            return suggestions[:3]  # Ensure we get exactly 3 suggestions
        except Exception as e:
            logger.error(f"Suggestions generation error: {str(e)}")
            return [
                "Break down your goals into smaller, achievable tasks",
                "Set specific deadlines for each milestone",
                "Track your progress regularly and adjust your approach as needed"
            ]
