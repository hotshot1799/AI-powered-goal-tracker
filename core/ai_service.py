from groq import Groq
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    async def analyze_progress(
        self, 
        progress_text: str, 
        goal_context: str
    ) -> float:
        """
        Analyzes progress update text and returns a progress percentage.
        
        Args:
            progress_text: The update text to analyze
            goal_context: Context about the goal for better analysis
            
        Returns:
            float: Progress percentage between 0 and 100
        """
        prompt = f"""
        Goal Context: {goal_context}
        Progress Update: {progress_text}
        Task: Calculate the percentage of progress towards this goal based on the update.
        Return only the numerical percentage between 0 and 100.
        """

        try:
            completion = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
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
            
            try:
                progress_value = float(response_text.strip())
                return max(0, min(100, progress_value))
            except ValueError:
                logger.error(f"Could not parse AI response as float: {response_text}")
                return 0.0
                
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return 0.0

    async def get_suggestions(
        self, 
        goals_data: str,
        num_suggestions: int = 3
    ) -> list[str]:
        """
        Generates AI-powered suggestions for goal achievement.
        
        Args:
            goals_data: String containing goals and their progress
            num_suggestions: Number of suggestions to generate
            
        Returns:
            list[str]: List of suggestions
        """
        prompt = f"""
        Based on these goals:
        {goals_data}
        
        Provide {num_suggestions} specific, actionable suggestions to help achieve these goals.
        Focus on practical next steps and motivation.
        Format each suggestion as a clear, encouraging statement.
        """

        try:
            completion = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
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
                
            suggestions = [s.strip() for s in response_text.split('\n') if s.strip()]
            return suggestions[:num_suggestions]
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return [
                "Break down your goals into smaller, manageable tasks",
                "Track your progress regularly",
                "Stay consistent with your efforts"
            ]
