import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

MODEL_PATH = "sec_iforest.pkl"
clf = None

def train_dummy_model():
    rng = np.random.RandomState(42)
    X = np.vstack([
        rng.normal(60, 10, 1000),
        rng.normal(8, 3, 1000),
        rng.randint(0,4,1000),
        rng.normal(1000,200,1000)
    ]).T

    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    print("✅ Security model trained")

def load_model():
    global clf
    if clf is None:
        if not os.path.exists(MODEL_PATH):
            train_dummy_model()
        clf = joblib.load(MODEL_PATH)
    return clf

def is_anomalous(speed, distance, antenna_id, dt):
    model = load_model()
    x = np.array([[speed, distance, antenna_id, dt]])
    return model.predict(x)[0] == -1
