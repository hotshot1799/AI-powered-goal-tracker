from groq import AsyncGroq
from core.config import settings
import logging
from datetime import datetime
from typing import List, Dict, Any
import json

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

    def _calculate_days_remaining(self, target_date: str) -> str:
        """Helper method to safely calculate days remaining until target date."""
        try:
            if not target_date:
                return "unknown"
            target = datetime.fromisoformat(target_date.rstrip('Z'))
            current = datetime.now()
            days = (target - current).days
            return str(days) if days >= 0 else "overdue"
        except Exception as e:
            logger.error(f"Error calculating days remaining: {str(e)}")
            return "unknown"

    async def get_personalized_suggestions(self, goals: List[Dict[str, Any]]) -> List[str]:
        """Generate personalized AI suggestions based on user's goals and context."""
        try:
            if not goals:
                return [
                    "Start by creating your first SMART goal - make it Specific, Measurable, Achievable, Relevant, and Time-bound",
                    "Think about what you want to achieve in different areas of your life: Health, Career, Personal Development",
                    "Consider breaking down your future goals into smaller, manageable milestones"
                ]

            # Format goals for the prompt
            goals_text = "\n\n".join([
                f"Goal {i+1}:\n"
                f"Category: {goal.get('category', 'Unknown')}\n"
                f"Description: {goal.get('description', 'No description')}\n"
                f"Progress: {goal.get('progress', 0)}%\n"
                f"Target Date: {goal.get('target_date', 'No date')}"
                for i, goal in enumerate(goals)
            ])

            prompt = f"""As an AI goal coach, analyze these goals and provide 3 specific, actionable suggestions:

{goals_text}

For each goal, consider:
1. Current progress and time remaining
2. The specific category requirements
3. Practical next steps
4. Any potential obstacles
5. Ways to maintain motivation

Format your response as exactly 3 distinct suggestions.
Make each suggestion specific to the actual goals described.
Start each suggestion with an action verb.
Include specific details from the goals.

Example format:
"Start working on [specific goal] by [specific action]..."
"Focus on improving [specific aspect] of [specific goal]..."
"Prioritize [specific task] to achieve [specific goal]..."

Avoid generic advice. Make sure each suggestion references specific goals and details."""

            # Get AI response
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
            
            # Process the response into separate suggestions
            raw_suggestions = [
                line.strip()
                for line in response_text.split('\n')
                if line.strip() and not line.strip().startswith(('•', '-', '*', '1.', '2.', '3.'))
            ]

            # Ensure we have at least 3 suggestions
            suggestions = []
            for suggestion in raw_suggestions:
                # Clean up the suggestion
                cleaned = suggestion.strip().strip('"').strip()
                if cleaned and len(cleaned) > 10:  # Avoid very short suggestions
                    suggestions.append(cleaned)
                if len(suggestions) >= 3:
                    break
                
            # If we don't have enough valid suggestions, add fallbacks
            while len(suggestions) < 3:
                suggestions.append("Break down your goals into smaller, manageable tasks")

            logger.info(f"Generated suggestions: {suggestions}")  # Add logging
            return suggestions[:3]

        except Exception as e:
            logger.error(f"Error in get_personalized_suggestions: {str(e)}")
            logger.error(f"Goals data: {goals}")  # Add logging
            return [
                "Break down your goals into smaller, manageable tasks",
                "Track your progress regularly",
                "Stay consistent with your efforts"
            ]

    async def analyze_progress(self, update_text: str, goal_description: str) -> dict:
        """
        Analyzes progress update text and returns progress percentage and analysis.
        
        Args:
            update_text: The update text to analyze
            goal_description: Context about the goal
            
        Returns:
            dict: Contains progress percentage and analysis
        """
        try:
            prompt = f"""Analyze this progress update for the goal:
            Goal: {goal_description}
            Update: {update_text}

            Provide:
            1. A percentage (0-100) estimating goal completion
            2. A brief analysis of the progress

            Return as JSON:
            {{
                "percentage": <number 0-100>,
                "analysis": "<brief explanation>"
            }}
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
            
            try:
                result = json.loads(response_text)
                result['percentage'] = max(0, min(100, float(result['percentage'])))
                return result
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"Error parsing AI response: {str(e)}")
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