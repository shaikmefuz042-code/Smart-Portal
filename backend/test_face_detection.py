import cv2

# Load face detector
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Load test image (group photo)
img = cv2.imread("group.jpg")   # put a group photo in backend folder
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detect faces
faces = face_cascade.detectMultiScale(gray, 1.3, 5)

# Draw rectangles
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

print(f"Faces detected: {len(faces)}")

# Show image
cv2.imshow("Detected Faces", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
