from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Training data: [speed, distance] -> collision(1) / safe(0)
X = np.array([[80,5],[100,2],[60,15],[30,25],[90,4],[40,20]])
y = np.array([1,1,0,0,1,0])

model = RandomForestClassifier()
model.fit(X, y)

def predict_collision(speed, distance):
    return model.predict([[speed, distance]])[0]
