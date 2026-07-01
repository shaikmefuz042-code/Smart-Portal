from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "../frontend"),
    static_folder=os.path.join(BASE_DIR, "../frontend")
)

# ---------------- MONGODB ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_portal"]

students = db["students"]
faculty = db["faculty"]
attendance = db["attendance"]

# ---------------- DATASET LOAD ----------------
DATASET_PATH = os.path.join(BASE_DIR, "dataset")

known_encodings = []
known_rolls = []

print("📂 Loading dataset from:", DATASET_PATH)

if os.path.exists(DATASET_PATH):
    for branch in os.listdir(DATASET_PATH):  # Loop through branches (e.g., CSBS)
        branch_path = os.path.join(DATASET_PATH, branch)
        if not os.path.isdir(branch_path):
            continue
        
        for img in os.listdir(branch_path):  # Images directly in branch folder
            if not img.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            roll = os.path.splitext(img)[0]  # Extract roll from filename (e.g., "231fa20020" from "231fa20020.jpg")
            path = os.path.join(branch_path, img)
            try:
                image = face_recognition.load_image_file(path)
                enc = face_recognition.face_encodings(image)
                if enc:
                    known_encodings.append(enc[0])
                    known_rolls.append(roll)
                    print(f"✅ Loaded face for roll: {roll} in branch: {branch}")
                else:
                    print(f"⚠️ No face encoding found in {path}")
            except Exception as e:
                print(f"❌ Error loading {path}: {e}")

if known_rolls:
    print("✅ Faces Loaded:", set(known_rolls))
else:
    print("❌ No faces loaded. Ensure structure: dataset/<branch>/<roll>.jpg (e.g., dataset/CSBS/231fa20020.jpg)")

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/faculty")
def faculty_page():
    faculty_id = request.args.get('id')
    if not faculty_id:
        return "Access Denied", 403
    return render_template("faculty_dashboard.html", faculty_id=faculty_id)

@app.route("/student")
def student_page():
    roll = request.args.get('roll')
    branch = request.args.get('branch')  # New: Get branch from URL
    if not roll or not branch:
        return "Access Denied", 403
    return render_template("student_dashboard.html", roll=roll, branch=branch)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return app.send_static_file(f'css/{filename}')

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role = data["role"]
    uid = data["id"]
    password = data["password"]
    branch = data.get("branch")  # New: Get branch for students

    if role == "faculty":
        user = faculty.find_one({"faculty_id": uid, "password": password})
        if user:
            return jsonify({"status": "success", "role": "faculty", "id": uid})

    if role == "student":
        user = students.find_one({"roll_no": uid, "password": password, "branch": branch.lower()})  # Use lowercase for MongoDB
        if user:
            return jsonify({"status": "success", "role": "student", "roll": uid, "branch": branch.lower()})

    return jsonify({"status": "fail"})

# ---------------- TOTAL CONDUCTED CLASSES ----------------
@app.route("/attendance/total-classes")
def total_classes():
    dates = attendance.distinct("date")
    return jsonify({"total": len(dates)})

# ---------------- MARK ATTENDANCE WITH SUBJECT ----------------
@app.route("/faculty/attendance", methods=["POST"])
def mark_attendance():
    file = request.files["image"]
    subject = request.form.get("subject")  # Get subject from form
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb)

    today = str(datetime.today().date())
    present_set = set()  # To prevent duplicates
    present_list = []

    for enc in encodings:
        distances = face_recognition.face_distance(known_encodings, enc)
        idx = np.argmin(distances)

        if distances[idx] < 0.55:
            roll = known_rolls[idx]
            if roll in present_set:  # Skip if already marked
                continue
            present_set.add(roll)
            
            student = students.find_one({"roll_no": roll})
            attendance.update_one(
                {"roll_no": roll, "date": today, "subject": subject},  # Include subject
                {"$set": {"status": "Present"}},
                upsert=True
            )

            present_list.append({
                "roll": roll,
                "name": student["name"] if student else "Unknown"
            })

    return jsonify(present_list)

# ---------------- STUDENT DATA ----------------
@app.route("/student/data/<roll>")
def student_data(roll):
    student = students.find_one({"roll_no": roll}, {"_id": 0, "password": 0})
    return jsonify(student or {})

# ---------------- STUDENT IMAGE ----------------
@app.route("/student/image/<roll>/<branch>")
def student_image(roll, branch):
    image_path = os.path.join(BASE_DIR, "dataset", branch.upper(), f"{roll}.jpg")  # Use uppercase for CSBS folder
    if os.path.exists(image_path):
        return app.send_file(image_path, mimetype='image/jpeg')
    return "Image not found", 404

# ---------------- FACULTY DATA ----------------
@app.route("/faculty/data/<faculty_id>")
def faculty_data(faculty_id):
    fac = faculty.find_one({"faculty_id": faculty_id}, {"_id": 0, "password": 0})
    return jsonify(fac or {})

# ---------------- ATTENDANCE DATA ----------------
@app.route("/attendance/<roll>")
def student_attendance(roll):
    records = list(attendance.find({"roll_no": roll}, {"_id": 0}))
    return jsonify(records)

# ---------------- STUDENTS BY YEAR AND BRANCH ----------------
@app.route("/students/<year>/<branch>")
def get_students(year, branch):
    studs = list(students.find({"year": year, "branch": branch}, {"roll_no": 1, "name": 1, "_id": 0}))  # Changed to lowercase "branch"
    return jsonify(studs)

# ---------------- FEE BALANCE ----------------
@app.route("/student/fee/<roll>")
def student_fee(roll):
    student = students.find_one({"roll_no": roll}, {"fee_balance": 1})
    return jsonify({"fee_balance": student.get("fee_balance", 0) if student else 0})

# ---------------- SUBJECTS BY YEAR AND BRANCH ----------------
@app.route("/subjects/<year>/<branch>")
def get_subjects(year, branch):
    subjects = list(db.subjects.find({"year": year, "branch": branch}, {"subject_code": 1, "subject_name": 1, "_id": 0}))
    return jsonify(subjects)

# ---------------- SECTION ATTENDANCE ----------------
@app.route("/attendance/section/<year>/<branch>")
def section_attendance(year, branch):
    studs = list(students.find({"year": year, "branch": branch}, {"roll_no": 1, "name": 1, "_id": 0}))  # Changed to lowercase "branch"
    subjects = list(db.subjects.find({"year": year, "branch": branch}, {"subject_code": 1, "_id": 0}))
    total_classes = attendance.distinct("date")
    total_count = len(total_classes)
    
    data = []
    for stud in studs:
        roll = stud["roll_no"]
        student_data = {"roll": roll, "name": stud["name"], "subjects": {}, "overall": 0}
        total_present = 0
        for subj in subjects:
            subj_code = subj["subject_code"]
            subj_records = list(attendance.find({"roll_no": roll, "subject": subj_code}))
            present = len([r for r in subj_records if r["status"] == "Present"])
            percentage = (present / total_count * 100) if total_count > 0 else 0
            student_data["subjects"][subj_code] = f"{percentage:.2f}%"
            total_present += present
        student_data["overall"] = f"{(total_present / (total_count * len(subjects)) * 100):.2f}%" if total_count > 0 else "0%"
        data.append(student_data)
    return jsonify(data)

# ---------------- STUDENT SUBJECT ATTENDANCE ----------------
@app.route("/attendance/student/<roll>")
def student_subject_attendance(roll):
    try:
        print(f"Request for roll: {roll}")
        # Get student's year and branch
        student = students.find_one({"roll_no": roll}, {"year": 1, "branch": 1})  # Changed to lowercase "branch"
        print(f"Student found: {student}")
        if not student:
            print(f"Student {roll} not found in database.")
            return jsonify([])  # Return empty if student not found
        
        year = student.get("year")
        branch = student.get("branch")  # Changed to lowercase "branch"
        print(f"Student {roll}: year={year}, branch={branch}")
        
        # Filter subjects by year and branch
        subjects = list(db.subjects.find({"year": year, "branch": branch}, {"subject_code": 1, "_id": 0}))
        print(f"Subjects query: year={year}, branch={branch}")
        print(f"Subjects found: {subjects}")
        
        total_classes = attendance.distinct("date")
        total_count = len(total_classes)
        print(f"Total classes: {total_count}")
        
        data = []
        for subj in subjects:
            subj_code = subj["subject_code"]
            records = list(attendance.find({"roll_no": roll, "subject": subj_code}))
            present = len([r for r in records if r["status"] == "Present"])
            percentage = (present / total_count * 100) if total_count > 0 else 0
            data.append({"subject": subj_code, "records": records, "percentage": f"{percentage:.2f}%"})
        print(f"Final data: {data}")
        return jsonify(data)
    except Exception as e:
        print(f"Error in student_subject_attendance: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)