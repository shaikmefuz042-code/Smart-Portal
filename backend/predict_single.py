import cv2
import tensorflow as tf
import numpy as np
import os

IMG_SIZE = 100

# Load model
model = tf.keras.models.load_model("../model/face_model.h5")

# Load labels
labels = sorted(os.listdir("../dataset"))

# Load test image
img = cv2.imread("test.jpg")   # put a face image here
face = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
face = face / 255.0
face = np.reshape(face, (1, IMG_SIZE, IMG_SIZE, 3))

prediction = model.predict(face)
idx = np.argmax(prediction)

print("Recognized Student:", labels[idx])
