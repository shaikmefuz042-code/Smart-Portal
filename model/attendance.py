import cv2
import numpy as np
import tensorflow as tf
import pandas as pd
from datetime import datetime

# Load model
model = tf.keras.models.load_model("face_model.h5")

# Labels (same as before)
labels = {0: "231fa20020", 1: "231fa20023", 2: "231fa20031"}

# Load face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Initialize attendance DataFrame
attendance_file = "attendance.csv"
try:
    df = pd.read_csv(attendance_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Roll Number", "Time", "Status"])

cap = cv2.VideoCapture(0)
print("📷 Press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (224, 224))
        face = face / 255.0
        face = np.expand_dims(face, axis=0)

        prediction = model.predict(face, verbose=0)
        class_id = np.argmax(prediction)
        confidence = np.max(prediction) * 100
        roll = labels[class_id]

        # Draw rectangle and label
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(frame, f"{roll} ({confidence:.2f}%)", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Mark attendance
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if roll not in df["Roll Number"].values:
            new_row = pd.DataFrame([{"Roll Number": roll, "Time": now, "Status": "Present"}])
            df = pd.concat([df, new_row], ignore_index=True)

    cv2.imshow("Smart Attendance", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Save attendance
df.to_csv(attendance_file, index=False)
print(f"✅ Attendance saved to {attendance_file}")
