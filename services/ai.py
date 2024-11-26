from groq import AsyncGroq
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        try:
            self.client = AsyncGroq(
                api_key=settings.GROQ_API_KEY,
                timeout=30.0
            )
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            raise

    async def analyze_data(self, prompt: str) -> str:
        try:
            chat_completion = await self.client.chat.completions.create(
                model="llama-3.2-11b-vision-preview", 
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=1,
                max_tokens=1000,
                top_p=1,
                stream=False
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            raise

    async def get_suggestions(self, goals: list) -> list:
        if not goals:
            return [
                "Start by setting a SMART goal - Specific, Measurable, Achievable, Relevant, and Time-bound",
                "Consider what you want to achieve in the next 3-6 months",
                "Break down your goals into smaller, manageable tasks"
            ]

        goals_text = "\n".join([
            f"Goal: {goal.description}\nCategory: {goal.category}\nTarget Date: {goal.target_date}"
            for goal in goals
        ])

        prompt = f"""
        Based on these goals:
        {goals_text}

        Provide 3 specific, actionable suggestions that:
        1. Help achieve these goals effectively
        2. Are practical and can be started immediately
        3. Consider the target dates mentioned

        Format: Provide exactly 3 suggestions, one per line.
        Keep each suggestion brief and actionable.
        """

        try:
            response = await self.analyze_data(prompt)
            # Split response into lines and clean them
            suggestions = [
                line.strip() for line in response.split('\n')
                if line.strip() and not line.startswith(('1.', '2.', '3.'))
            ]
            
            # Ensure we have exactly 3 suggestions
            while len(suggestions) < 3:
                suggestions.append("Set regular check-ins to track your progress")
                
            return suggestions[:3]
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {str(e)}")
            return [
                f"For your {goals[0].category} goal: Break down tasks into weekly milestones",
                "Create a daily action plan for each goal",
                "Schedule regular progress reviews"
            ]
