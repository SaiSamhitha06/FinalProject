from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json
import os
import smtplib
from email.message import EmailMessage
from chatbot import chatbot_response

app = Flask(__name__, template_folder="templates", static_folder="static")

CORS(app)

app.secret_key = "76f4c00a15ebee42bf4772e8c1f8fa5220285117af40933c9ca738e78410d468"

# Email Credentials (use environment variables)
EMAIL_ADDRESS = os.getenv("manvikjaiyashoraam@gmail.com")
EMAIL_PASSWORD = os.getenv("tokp hrib yzew pktk")

# Ensure necessary folders exist
os.makedirs("data", exist_ok=True)

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_FILE = os.path.join(BASE_DIR, "data", "notes_data.json")
ASSIGNMENT_FILE = os.path.join(BASE_DIR, "data", "assignments.json")
SURVEY_FILE = os.path.join(BASE_DIR, "data", "surveys.json")
STUDENT_FILE = os.path.join(BASE_DIR, "data", "students.json")
FACULTY_FILE = os.path.join(BASE_DIR, "data", "faculty.json")

#loading
def load_json(filename):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                # Convert single dict to list
                return [data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

#saving
def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# Serve Upload Notes Page
@app.route('/upload_notes.html', methods=['GET'])
def upload_notes_page():
    return render_template('upload_notes.html')


# Upload Notes API
@app.route('/upload_notes', methods=['POST'])
def upload_file():
    subject = request.form.get("subject")
    date = request.form.get("date")
    drive_link = request.form.get("drive_link")

    if not subject or not date or not drive_link:
        return jsonify({"message": "All fields are required!"}), 400

    notes = load_json(NOTES_FILE)
    if any(note["subject"].lower() == subject.lower() and note["date"] == date for note in notes):
        return jsonify({"message": "Notes for this subject and date already exist!"}), 400

    notes.append({"subject": subject.lower(), "date": date, "link": drive_link})
    save_json(NOTES_FILE, notes)

    return jsonify({"message": "File uploaded successfully!"})


# Chatbot API
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    response = chatbot_response(user_input)
    return jsonify({"response": response})


# Faculty Login
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    faculty_data = load_json(FACULTY_FILE)
    if any(user["email"] == email and user["password"] == password for user in faculty_data):
        session["logged_in"] = True
        session["email"] = email
        return redirect(url_for("uploads"))

    return jsonify({"message": "Invalid credentials. Please try again."}), 400


# Faculty Dashboard
@app.route("/uploads")
def uploads():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))
    return render_template("uploads.html")


# Logout
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("email", None)
    return redirect(url_for("login_page"))


# Email Notification
# Email Notification
def send_email(teacher_email, subject, message):
    student_emails = load_json(STUDENT_FILE)
    if not student_emails:
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = teacher_email
    msg["To"] = ", ".join(student_emails)
    msg.set_content(message)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("saisamhithanadipena@gmail.com", "pqlc fcmt zurk lmbi")
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")



# Handle Assignment Upload
@app.route("/upload_assignment", methods=["POST"])
def handle_upload_assignment():
    teacher_email = request.form.get("teacher_email")
    class_name = request.form.get("class_name")
    assignment_link = request.form.get("assignment_link")
    subject = request.form.get("subject")


    if not teacher_email or not class_name or not assignment_link:
        return jsonify({"error": "Missing data"}), 400

    # Load existing assignments as a list
    assignments = load_json(ASSIGNMENT_FILE)

    assignment_data = {
        "teacher_email": teacher_email,
        "class_name": class_name,
        "assignment_link": assignment_link,
        "subject" : subject
    }

    # Add new assignment to the list
    assignments.append(assignment_data)
    save_json(ASSIGNMENT_FILE, assignments)

    send_email(
        f"{subject} Assignment",
        f"New Assignment for {class_name}!",
        f"A new assignment has been uploaded.\nLink: {assignment_link}",
    )

    return jsonify({"message": "Assignment uploaded and notification sent!"}), 200


# Handle Survey Upload
@app.route("/upload_survey", methods=["POST"])
def handle_upload_survey():
    teacher_email = request.form.get("teacher_email")
    class_name = request.form.get("class_name")
    section = request.form.get("section")
    survey_link = request.form.get("survey_link")

    if not teacher_email or not class_name or not section or not survey_link:
        return jsonify({"error": "Missing data"}), 400

    surveys = load_json(SURVEY_FILE)
    survey_data = {"teacher_email": teacher_email, "class_name": class_name, "section": section, "survey_link": survey_link}
    surveys.append(survey_data)
    save_json(SURVEY_FILE, surveys)

    send_email(teacher_email, f"New Survey for {class_name} - {section}", f"A new survey has been uploaded.\nLink: {survey_link}")

    return jsonify({"message": "Survey uploaded and notification sent!"}), 200


# Serve HTML Pages
@app.route('/')
def index_page():
    return render_template("index.html")

@app.route('/login_page')
def login_page():
    return render_template("login.html")




@app.route('/upload_assignment')
def upload_assignment_page():
    return render_template('upload_assignment.html')


@app.route('/upload_survey.html')
def upload_survey_page():
    return render_template('upload_survey.html')


if __name__ == "__main__":
    app.run(debug=True, port=5000)
