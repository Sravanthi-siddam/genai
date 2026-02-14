import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# Create a simple dummy model
def create_dummy_model():
    model = models.Sequential([
        layers.Input(shape=(224, 224, 3)),
        layers.Conv2D(16, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(4, activation='softmax')  # 4 classes to match our mock data
    ])
    
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    # Save the model
    model.save('model.h5')
    print("Dummy model saved as model.h5")

if __name__ == "__main__":
    create_dummy_model()
