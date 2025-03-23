import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import LabelEncoder
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt')

# Load dataset
with open("chatbot_dataset.json", "r") as file:
    data = json.load(file)

# Extract inputs & labels
questions = []
labels = []
responses = {}

for item in data["data"]:
    questions.append(item["question"])
    labels.append(item["tag"])
    responses[item["tag"]] = item["response"]

# Tokenization
words = []
for question in questions:
    words.extend(word_tokenize(question.lower()))

words = sorted(set(words))

# Encode labels
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

# Create training data
X_train, y_train = [], []
for question, label in zip(questions, encoded_labels):
    tokens = word_tokenize(question.lower())
    bag = [1 if w in tokens else 0 for w in words]
    X_train.append(bag)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

# Convert to PyTorch tensors
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)

# Define ANN Model
class ChatbotModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(ChatbotModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Initialize model
input_size = len(words)
hidden_size = 8
output_size = len(set(labels))

model = ChatbotModel(input_size, hidden_size, output_size)

# Loss and Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Training Loop
epochs = 100
for epoch in range(epochs):
    optimizer.zero_grad()
    outputs = model(X_train_tensor)
    loss = criterion(outputs, y_train_tensor)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# Save model
torch.save(model.state_dict(), "chatbot_model.pth")
print("Model training complete!")
