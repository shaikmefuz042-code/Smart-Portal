import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Input

DATASET_PATH = r"E:\smart portal\dataset"
IMG_SIZE = (224, 224)
BATCH_SIZE = 4
EPOCHS = 10

datagen = ImageDataGenerator(rescale=1./255)

train = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

print("Classes found:", train.class_indices)

model = Sequential([
    Input(shape=(224, 224, 3)),
    Conv2D(32, (3,3), activation="relu"),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(128, activation="relu"),
    Dense(train.num_classes, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(train, epochs=EPOCHS)

model.save("face_model.h5")
print("✅ Model trained and saved as face_model.h5")
