import json
import torch
import nltk
from flask import Flask, request, jsonify
from nltk.tokenize import word_tokenize
import numpy as np
import os
from datetime import datetime
from train_chatbot import ChatbotModel, words, label_encoder, responses

app = Flask(__name__)

# Load trained model
model = ChatbotModel(len(words), 8, len(responses))
model.load_state_dict(torch.load("chatbot_model.pth"))  # Ensure correct path
model.eval()

# File path for notes data
NOTES_FILE = "data/notes_data.json"

# Function to load existing notes
def load_notes():
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r") as file:
                notes = json.load(file)
                if isinstance(notes, list):
                    return notes
                else:
                    print("Error: notes_data.json is not in a valid format.")
                    return []
        except json.JSONDecodeError:
            print("Error: notes_data.json is corrupted.")
            return []
    return []

# Function to extract a valid date from user input
def extract_date_from_input(tokens):
    for word in tokens:
        try:
            return datetime.strptime(word, "%d-%m-%Y").strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD format
        except ValueError:
            continue  # Ignore if not a date
    return None

# Dictionary of quiz links
QUIZ_LINKS = {
    "ai": "https://www.sanfoundry.com/artificial-intelligence-questions-answers/",
    "ml": "https://www.sanfoundry.com/artificial-intelligence-questions-answers/",
    "deep learning": "https://www.sanfoundry.com/artificial-intelligence-questions-answers/",
    "reinforcement learning": "https://www.sanfoundry.com/artificial-intelligence-questions-answers/",
    "dbms": "https://www.sanfoundry.com/database-management-system-questions-answers/",
    "java": "https://www.sanfoundry.com/java-programming-questions-answers/",
    "data structures": "https://www.sanfoundry.com/data-structure-questions-answers/",
    "python": "https://www.sanfoundry.com/1000-python-questions-answers/",
}

# Function to get chatbot response (including quiz, notes, and normal response)
def chatbot_response(user_input):
    tokens = word_tokenize(user_input.lower())

    # Quiz feature
    if "quiz" in tokens:
        for subject in QUIZ_LINKS.keys():
            if subject in user_input.lower():
                return f"{subject.capitalize()} Quiz → [Click Here]({QUIZ_LINKS[subject]})"
        return "Sorry, I couldn't find a quiz for that subject."

    # Notes feature
    notes = load_notes()
    if "notes" in tokens:
        if not notes:
            return "No notes have been uploaded yet."

        user_subject = user_input.lower()
        user_date = extract_date_from_input(tokens)  # Extract date if provided

        for note in notes:
            subject_match = note["subject"].lower() in user_subject
            date_match = (user_date is None or note["date"] == user_date)

            if subject_match and date_match:
                return f"Notes for {note['subject'].capitalize()} on {note['date']} are available.\n Click the link to access: {note['link']}"

        return "Sorry, no matching notes found."

    # Default chatbot response
    bag = np.array([1 if w in tokens else 0 for w in words], dtype=np.float32)
    input_tensor = torch.tensor([bag])

    output = model(input_tensor)
    _, predicted = torch.max(output, dim=1)
    tag = label_encoder.inverse_transform([predicted.item()])[0]

    return responses.get(tag, "Sorry, I don't understand.")

# Survey links feature
DATABASE_FILE = "data/survey_links.json"

def load_surveys():
    """Load survey links from a JSON file."""
    try:
        with open(DATABASE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Chatbot API to respond to user queries."""
    data = request.json
    user_message = data.get("message", "").lower()

    if "survey" in user_message:
        words = user_message.split()
        for word in words:
            class_name = word.upper()  # Assuming class names are in uppercase
            surveys = load_surveys()
            if class_name in surveys:
                return jsonify({"response": f"The survey link for {class_name} is {surveys[class_name]}"})

        return jsonify({"response": "I couldn't find a survey for your class. Please check with your teacher."})

    return jsonify({"response": chatbot_response(user_message)})

# Prevent script from running when imported
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        response = chatbot_response(user_input)
        print("Bot:", response)
