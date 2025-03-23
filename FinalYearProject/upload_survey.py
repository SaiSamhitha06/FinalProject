from flask import Flask, request, jsonify
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # Enable CORS for frontend requests

DATA_FILE = "students_data.json"

def load_data():
    """Loads stored data from JSON file."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(data):
    """Saves updated data back to JSON."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

@app.route("/upload-survey", methods=["POST"])
def upload_survey():
    """Handles survey link uploads from teachers."""
    data = request.get_json()
    course_name = data.get("course_name")
    survey_link = data.get("survey_link")

    if not course_name or not survey_link:
        return jsonify({"message": "Both fields are required!"}), 400

    dataset = load_data()
    
    if "course_exit_surveys" not in dataset:
        dataset["course_exit_surveys"] = {}

    dataset["course_exit_surveys"][course_name] = survey_link
    save_data(dataset)

    return jsonify({"message": f"Survey for {course_name} uploaded successfully!"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
