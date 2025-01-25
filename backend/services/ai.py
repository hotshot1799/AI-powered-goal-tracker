from groq import AsyncGroq
from core.config import settings
import logging
import json
from typing import List, Dict, Any

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

    async def get_personalized_suggestions(self, goals: List[Dict[str, Any]], user_context: Dict[str, Any] = None) -> List[str]:
        """
        Generate personalized AI suggestions based on user's goals and context.
        
        Args:
            goals: List of user's goals with their details and progress
            user_context: Optional additional context about the user
            
        Returns:
            List[str]: List of personalized suggestions
        """
        try:
            # Format goals data for the prompt
            goals_context = "\n".join([
                f"Goal {i+1}:"
                f"\n- Category: {goal.get('category')}"
                f"\n- Description: {goal.get('description')}"
                f"\n- Progress: {goal.get('progress', 0)}%"
                f"\n- Target Date: {goal.get('target_date')}"
                for i, goal in enumerate(goals)
            ])

            # Construct a detailed prompt for better suggestions
            prompt = f"""
            Based on the following goals and their current progress:

            {goals_context}

            Please provide 3 specific, actionable, and personalized suggestions that:
            1. Address the goals with lower progress first
            2. Consider the target dates and urgency
            3. Provide practical next steps
            4. Include motivation and accountability elements
            5. Consider relationships between different goals if any exist

            Format each suggestion to be clear, encouraging, and immediately actionable.
            Focus on what the user can do today or this week to make progress.
            """

            chat_completion = await self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False
            )

            response_text = chat_completion.choices[0].message.content.strip()
            
            # Process and clean up suggestions
            suggestions = [
                suggestion.strip()
                for suggestion in response_text.split('\n')
                if suggestion.strip() and not suggestion.startswith(('1.', '2.', '3.', '-', '*'))
            ]

            # Ensure we return exactly 3 suggestions
            if len(suggestions) < 3:
                suggestions.extend([
                    "Break down your goals into smaller, manageable tasks",
                    "Track your progress regularly",
                    "Stay consistent with your efforts"
                ][:3 - len(suggestions)])
            
            return suggestions[:3]

        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return [
                "Break down your goals into smaller, manageable tasks",
                "Track your progress regularly",
                "Stay consistent with your efforts"
            ]

    async def analyze_progress(self, update_text: str, goal_description: str) -> dict:
        """
        Analyzes a progress update and returns progress percentage and analysis.
        
        Args:
            update_text: The progress update text
            goal_description: The goal being tracked
            
        Returns:
            dict: Contains progress percentage and analysis
        """
        try:
            prompt = f"""
            Goal: {goal_description}
            Progress Update: {update_text}

            Based on this progress update, please provide:
            1. A percentage (0-100) indicating goal completion progress
            2. A brief analysis explaining the progress evaluation

            Return the response in this JSON format:
            {{
                "percentage": <number between 0-100>,
                "analysis": "<brief explanation>"
            }}
            """

            chat_completion = await self.client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Using Mixtral model for better analysis
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                stream=False
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            try:
                # Parse the JSON response
                result = json.loads(response_text)
                # Ensure percentage is within bounds
                result['percentage'] = max(0, min(100, float(result['percentage'])))
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON: {response_text}")
                return {
                    "percentage": 0,
                    "analysis": "Unable to analyze progress"
                }
                
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return {
                "percentage": 0,
                "analysis": "Error analyzing progress"
            }

    async def analyze_data(self, prompt: str) -> str:
        try:
            chat_completion = await self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                stream=False
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            raise