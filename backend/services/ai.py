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
        """
        Generate personalized AI suggestions based on user's goals and context.
        
        Args:
            goals: List of user's goals with their details and progress
            
        Returns:
            List[str]: List of personalized suggestions
        """
        try:
            if not goals:
                return [
                    "Start by creating your first SMART goal - make it Specific, Measurable, Achievable, Relevant, and Time-bound",
                    "Think about what you want to achieve in different areas of your life: Health, Career, Personal Development",
                    "Consider breaking down your future goals into smaller, manageable milestones"
                ]

            # Sort goals by priority (lower progress and closer deadlines first)
            sorted_goals = sorted(goals, 
                key=lambda x: (
                    x.get('progress', 0),  # Lower progress first
                    x.get('target_date', '9999')  # Closer deadlines first
                )
            )

            # Format goals data for the prompt
            current_date = datetime.now().isoformat()
            goals_context = "\n".join([
                f"Goal {i+1}:"
                f"\n- Category: {goal.get('category')}"
                f"\n- Description: {goal.get('description')}"
                f"\n- Current Progress: {goal.get('progress', 0)}%"
                f"\n- Target Date: {goal.get('target_date')}"
                f"\n- Days Remaining: {self._calculate_days_remaining(goal.get('target_date'))}"
                f"\n- Progress Trend: {goal.get('progress_trend', 'not available')}"
                for i, goal in enumerate(sorted_goals)
            ])

            prompt = f"""You are a highly capable AI goal coach. Given these goals:

            {goals_context}

            Today's Date: {current_date}

            Provide 3 highly personalized, actionable suggestions. For each suggestion:
            1. Consider both progress and time remaining
            2. Focus on goals that need immediate attention (low progress or close deadlines)
            3. Reference specific goal details in your suggestions
            4. Provide concrete next steps and mini-milestones
            5. Consider the goal categories and their requirements
            6. If a goal is behind schedule, provide catch-up strategies
            7. If a goal is on track, suggest ways to maintain momentum
            8. Where possible, suggest how to handle multiple goals efficiently

            Format each suggestion as a clear, actionable statement.
            Use specific details from the goals in your suggestions.
            Make suggestions time-sensitive based on deadlines.
            Include measurable mini-targets where appropriate.
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

            # Ensure we have exactly 3 suggestions
            while len(suggestions) < 3:
                suggestions.append("Break down your goals into smaller, manageable tasks")
            
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