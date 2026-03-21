import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import matplotlib.pyplot as plt

# Check if data exists
if not os.path.exists('training/engagement_data.csv'):
    print("ERROR: No data found. Run '1_collect_data.py' first!")
    exit()

# 1. Load Data
print("Loading Dataset...")
df = pd.read_csv('training/engagement_data.csv')

X = df.drop('class', axis=1) # Features
y = df['class'] # Target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Build Neural Network
model = Sequential([
    Dense(128, input_dim=132, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid') # Binary output
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 3. Train (THE EPOCHS)
print("Starting Training for 50 Epochs...")
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# 4. Save Model
if not os.path.exists('models'): os.makedirs('models')
model.save('models/custom_engagement_model.h5')
print("=== SUCCESS: Model saved to 'models/custom_engagement_model.h5' ===")

# 5. Show Graphs
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Accuracy over Epochs')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Loss over Epochs')
plt.legend()
plt.show()