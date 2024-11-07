# ai_analysis.py
import os
from flask import Flask, request, jsonify
from groq import Groq

# Initialize the Flask app
app = Flask(__name__)

# Hard-coded API key
API_KEY = "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"  # Replace with your actual API key

# Initialize Groq client
client = Groq()

# Route for AI analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    # Get data from the request
    data = request.json.get("data", "")
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Call the Groq model
    try:
        response = analyze_data(data)
        return jsonify({"result": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to perform AI analysis with Groq
def analyze_data(data):
    # Set up the completion call with Groq's Llama model
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": data}],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    # Stream and collect response
    response_text = ""
    for chunk in completion:
        response_text += chunk.choices[0].delta.content or ""
    
    return response_text

# Start the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
