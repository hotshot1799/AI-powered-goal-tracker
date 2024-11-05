from datetime import datetime
import speech_recognition as sr
import os
import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
headers = {"Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY')}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def analyze_data(goals):
    insights = []
    today = datetime.now().date()
    
    for goal in goals:
        target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d').date()
        days_left = (target_date - today).days
        
        if days_left < 0:
            insights.append(f"Goal '{goal['description']}' in category '{goal['category']}' is overdue.")
        elif days_left == 0:
            insights.append(f"Today is the target date for your goal: '{goal['description']}'!")
        elif days_left <= 7:
            insights.append(f"You have {days_left} days left for: '{goal['description']}'.")
            
    prompt = f"Analyze these goals and provide insights: {insights}"
    ai_insights = query({"inputs": prompt})
    
    return {"insights": ai_insights}

def suggest_goal_achievement(goal):
    prompt = f"""
    Provide 3 practical suggestions to achieve this goal:
    Category: {goal['category']}
    Description: {goal['description']}
    Target Date: {goal['target_date']}
    """
    
    suggestions = query({"inputs": prompt})
    return suggestions

def analyze_user_input(goal, user_input, input_type):
    prompt = f"""
    Goal: {goal['description']}
    User Update: {user_input}
    
    Analyze this update and provide:
    1. Progress assessment
    2. Encouragement
    3. Next steps
    """
    
    analysis = query({"inputs": prompt})
    return {"analysis": analysis}

def speech_to_text(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Speech was unclear"
        except sr.RequestError:
            return "Could not process speech"
