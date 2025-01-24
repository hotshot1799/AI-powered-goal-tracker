# backend/services/ai.py
from groq import AsyncGroq
from core.config import settings
import logging
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