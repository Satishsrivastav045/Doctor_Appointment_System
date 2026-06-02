import pickle
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"


def load_model():
    with MODEL_PATH.open("rb") as file:
        return pickle.load(file)


def predict_disease(data):
    model = load_model()
    symptoms = model["symptoms"]
    disease_counts = model["disease_counts"]
    symptom_presence = model["symptom_presence"]
    total_rows = model["total_rows"]

    scores = {}
    for disease, count in disease_counts.items():
        prior = count / total_rows
        score = prior
        for symptom, value in zip(symptoms, data):
            present_count = symptom_presence[disease].get(symptom, 0)
            present_prob = (present_count + 1) / (count + 2)
            absent_prob = 1 - present_prob
            score *= present_prob if value else absent_prob
        scores[disease] = score

    prediction = max(scores, key=scores.get)
    total_score = sum(scores.values()) or 1
    confidence = scores[prediction] / total_score
    return prediction, confidence
