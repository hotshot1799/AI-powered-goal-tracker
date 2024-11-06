import requests
import os
from datetime import datetime

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
headers = {"Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY')}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def analyze_user_input(goal, user_input):
    prompt = f"""
    Analyze this progress update for the following goal:
    Goal: {goal['description']}
    Category: {goal['category']}
    Update: {user_input}
    
    Provide:
    1. Progress assessment
    2. Constructive feedback
    3. Next steps suggestion
    """
    
    try:
        response = query({
            "inputs": prompt,
            "parameters": {"max_length": 300}
        })
        return {"analysis": response[0]['generated_text']}
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        return {"analysis": "Unable to analyze update at this time."}

def analyze_data(goal_data):
    prompt = f"""
    Analyze progress for this goal:
    Description: {goal_data['description']}
    Category: {goal_data['category']}
    Target Date: {goal_data['target_date']}
    
    Estimate current progress as a percentage (0-100) and provide insights.
    """
    
    try:
        response = query({
            "inputs": prompt,
            "parameters": {"max_length": 300}
        })
        # Extract percentage from response
        text = response[0]['generated_text']
        import re
        numbers = re.findall(r'(\d+)(?:\.?\d*)?%|\b(\d+)(?:\.?\d*)?\b', text)
        progress = float(numbers[0][0] or numbers[0][1]) if numbers else 0
        progress = min(100, max(0, progress))
        
        return {
            "progress": progress,
            "insights": [text]
        }
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        return {
            "progress": 0,
            "insights": ["Unable to analyze progress at this time."]
        }

def suggest_goal_achievement(goal):
    prompt = f"""
    Suggest ways to achieve this goal:
    Category: {goal['category']}
    Description: {goal['description']}
    
    Provide 3 specific, actionable suggestions.
    """
    
    try:
        response = query({
            "inputs": prompt,
            "parameters": {"max_length": 300}
        })
        suggestions = response[0]['generated_text'].split('\n')
        return [s.strip() for s in suggestions if s.strip()]
    except Exception as e:
        print(f"Error generating suggestions: {str(e)}")
        return ["Unable to generate suggestions at this time."]
