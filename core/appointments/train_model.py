import csv
import pickle
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "model.pkl"


def train():
    rows = []
    with DATASET_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)

    symptoms = [field for field in rows[0].keys() if field != "disease"]
    disease_counts = Counter()
    symptom_presence = defaultdict(lambda: defaultdict(int))

    for row in rows:
        disease = row["disease"]
        disease_counts[disease] += 1
        for symptom in symptoms:
            symptom_presence[disease][symptom] += int(row[symptom])

    model = {
        "symptoms": symptoms,
        "disease_counts": dict(disease_counts),
        "symptom_presence": {disease: dict(values) for disease, values in symptom_presence.items()},
        "total_rows": len(rows),
    }

    with MODEL_PATH.open("wb") as file:
        pickle.dump(model, file)

    print(f"Pure Python model trained and saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
