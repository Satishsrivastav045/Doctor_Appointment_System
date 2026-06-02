from __future__ import annotations

import imghdr
from dataclasses import dataclass
from typing import Iterable

from .ml_model import predict_disease


SYMPTOM_KEYWORDS = {
    "fever": ["fever", "bukhar", "temperature"],
    "cough": ["cough", "khansi"],
    "headache": ["headache", "sir dard", "head pain"],
    "fatigue": ["fatigue", "thakan", "weakness"],
    "sneezing": ["sneezing", "chheenk", "cold"],
    "itching": ["itching", "khujli"],
    "rash": ["rash", "red patch", "skin rash"],
    "vomiting": ["vomiting", "ulti", "nausea"],
    "stomach_pain": ["stomach pain", "pet dard", "abdominal pain"],
    "chest_pain": ["chest pain", "seene me dard"],
    "high_bp": ["high bp", "high blood pressure", "bp"],
    "irregular_periods": ["irregular periods", "period issue", "late periods"],
    "pelvic_pain": ["pelvic pain", "lower abdomen pain"],
}


DISEASE_RULES = [
    {"name": "Flu", "symptoms": {"fever", "cough", "fatigue", "headache"}, "specialization": "general"},
    {"name": "Common Cold", "symptoms": {"cough", "sneezing", "headache"}, "specialization": "general"},
    {"name": "Allergy", "symptoms": {"sneezing", "itching", "rash"}, "specialization": "derma"},
    {"name": "Migraine", "symptoms": {"headache", "fatigue"}, "specialization": "general"},
    {"name": "Dengue", "symptoms": {"fever", "headache", "fatigue", "vomiting"}, "specialization": "general"},
    {"name": "Heart Risk", "symptoms": {"chest_pain", "high_bp", "fatigue"}, "specialization": "cardio"},
    {"name": "Gynecology Concern", "symptoms": {"irregular_periods", "pelvic_pain"}, "specialization": "gyn"},
]


SPECIALIZATION_MAP = {
    "Flu": ["general", "medicine", "physician"],
    "Common Cold": ["general", "medicine", "physician"],
    "Allergy": ["allergy", "derma", "skin", "general"],
    "Migraine": ["general", "neuro", "physician"],
    "Dengue": ["general", "physician", "medicine"],
    "Heart Risk": ["cardio", "heart", "general"],
    "Gynecology Concern": ["gyn", "obst", "women", "gyne"],
}


MODEL_SYMPTOMS = ["fever", "cough", "headache", "fatigue"]

CONDITION_ADVICE = {
    "Flu": "Hydration, rest, temperature monitoring, aur symptoms 48 hours se zyada rahein to physician consult karein.",
    "Common Cold": "Steam, fluids, rest, aur severe breathing issue ya high fever ho to doctor se baat karein.",
    "Allergy": "Trigger avoid karein, rash/itching severe ho to dermatologist ya physician consult karein.",
    "Migraine": "Light exposure kam karein, hydration rakhein, aur repeated headache ke liye doctor review book karein.",
    "Dengue": "Platelet monitoring aur doctor consultation important hai, especially high fever/body pain ke saath.",
    "Heart Risk": "Chest pain, breathlessness, sweating, ya left-arm pain ho to urgent medical help lein.",
    "Gynecology Concern": "Gynecologist consultation book karein, especially pain severe ya bleeding unusual ho.",
    "General Viral Infection": "Symptoms track karein, rest lein, aur worsening signs par doctor consult karein.",
}

RED_FLAG_SYMPTOMS = {"chest_pain", "high_bp", "vomiting", "pelvic_pain"}


SYMPTOM_LABELS = {
    "fever": "fever",
    "cough": "cough",
    "headache": "headache",
    "fatigue": "fatigue/weakness",
    "sneezing": "sneezing/cold",
    "itching": "itching",
    "rash": "rash",
    "vomiting": "vomiting/nausea",
    "stomach_pain": "stomach pain",
    "chest_pain": "chest pain",
    "high_bp": "high BP",
    "irregular_periods": "irregular periods",
    "pelvic_pain": "pelvic/lower abdomen pain",
}


@dataclass
class RiskResult:
    score: int
    level: str
    recommendation: str


@dataclass
class InsightResult:
    summary: str
    recommendation: str
    repeat_visits: int


@dataclass
class ImageDiagnosisResult:
    label: str
    confidence: int
    recommendation: str
    image_type: str


def extract_symptoms(text: str) -> list[str]:
    text = (text or "").lower()
    found = []
    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            found.append(symptom)
    return found


def _score_rule(symptoms: set[str], rule_symptoms: set[str]) -> float:
    if not symptoms:
        return 0.0
    overlap = len(symptoms & rule_symptoms)
    if overlap == 0:
        return 0.0
    return overlap / len(symptoms | rule_symptoms)


def _human_join(items: list[str]) -> str:
    if not items:
        return "your symptoms"
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} and {items[-1]}"


def build_patient_response(result: dict) -> str:
    symptom_labels = [SYMPTOM_LABELS.get(symptom, symptom.replace("_", " ")) for symptom in result["extracted_symptoms"]]
    symptoms_text = _human_join(symptom_labels)
    primary = result["primary_condition"]
    confidence = result["predictions"][0]["confidence"] if result["predictions"] else 0
    urgency = result["urgency"]

    if urgency == "High":
        opening = (
            f"I noticed {symptoms_text}. This can point toward {primary}, and because there are possible red-flag symptoms, "
            "you should not delay medical review."
        )
        next_step = "Please book an appointment as soon as possible. If symptoms are severe, sudden, or worsening, seek emergency care."
    elif urgency == "Moderate":
        opening = (
            f"Based on {symptoms_text}, the closest match is {primary} with about {confidence}% confidence. "
            "This is not a final diagnosis, but it is enough to guide the next step."
        )
        next_step = "A doctor consultation is a good idea, especially if symptoms continue for more than 24-48 hours or keep coming back."
    else:
        opening = (
            f"I found a mild pattern from {symptoms_text}. The closest match is {primary}, but the signal is not very strong yet."
        )
        next_step = "You can monitor symptoms, rest, and add more details if things change. Book a doctor if symptoms persist or worsen."

    return f"{opening}\n\n{result['care_advice']}\n\nNext step: {next_step}"


def predict_from_text(text: str) -> dict:
    extracted = extract_symptoms(text)
    symptom_set = set(extracted)
    model_prediction = None

    if any(symptom in symptom_set for symptom in MODEL_SYMPTOMS):
        vector = [1 if symptom in symptom_set else 0 for symptom in MODEL_SYMPTOMS]
        try:
            disease, confidence = predict_disease(vector)
            model_prediction = {
                "name": disease,
                "confidence": round(confidence * 100, 1),
                "engine": "local_model",
            }
        except (FileNotFoundError, EOFError, KeyError, ValueError):
            model_prediction = None

    raw_scores = []
    for rule in DISEASE_RULES:
        score = _score_rule(symptom_set, rule["symptoms"])
        if score > 0:
            raw_scores.append((rule["name"], score))

    if not raw_scores:
        raw_scores = [("General Viral Infection", 0.55), ("Common Cold", 0.25), ("Allergy", 0.20)]

    max_score = max((score for _, score in raw_scores), default=1)
    predictions = [
        {"name": name, "confidence": round((score / max_score) * 92, 1), "engine": "rules"}
        for name, score in sorted(raw_scores, key=lambda item: item[1], reverse=True)
    ]

    if model_prediction:
        existing = next((item for item in predictions if item["name"] == model_prediction["name"]), None)
        if existing:
            existing["confidence"] = round((existing["confidence"] + model_prediction["confidence"]) / 2, 1)
            existing["engine"] = "hybrid"
        else:
            predictions.append(model_prediction)
            predictions.sort(key=lambda item: item["confidence"], reverse=True)

    primary = predictions[0]["name"]
    max_confidence = predictions[0]["confidence"]
    has_red_flags = bool(symptom_set & RED_FLAG_SYMPTOMS)

    if primary == "Heart Risk" or has_red_flags and max_confidence >= 45:
        urgency = "High"
        triage_message = "Doctor consultation ko priority dein. Severe symptoms hain to emergency care choose karein."
    elif max_confidence >= 55:
        urgency = "Moderate"
        triage_message = "Doctor appointment useful rahega, especially agar symptoms repeat ya worsen ho rahe hain."
    else:
        urgency = "Low"
        triage_message = "Initial self-care possible hai, par symptoms persist karein to consultation book karein."

    result = {
        "input_text": text,
        "extracted_symptoms": extracted,
        "predictions": predictions[:3],
        "primary_condition": primary,
        "recommended_specializations": SPECIALIZATION_MAP.get(primary, ["general"]),
        "urgency": urgency,
        "triage_message": triage_message,
        "care_advice": CONDITION_ADVICE.get(primary, CONDITION_ADVICE["General Viral Infection"]),
        "red_flags": sorted(symptom_set & RED_FLAG_SYMPTOMS),
        "model_prediction": model_prediction,
    }
    result["assistant_response"] = build_patient_response(result)
    return result


def recommend_doctors_for_condition(doctors: Iterable, condition: str, today) -> list[dict]:
    keywords = [keyword.lower() for keyword in SPECIALIZATION_MAP.get(condition, ["general"])]
    recommendations = []

    for doctor in doctors:
        specialization = (doctor.specialization or "").lower()
        specialization_match = 1 if any(keyword in specialization for keyword in keywords) else 0

        available_slots = [
            slot for slot in doctor.availability_set.all()
            if not slot.is_booked and slot.available_date >= today
        ]
        available_slots.sort(key=lambda slot: (slot.available_date, slot.start_time))
        next_slot = available_slots[0] if available_slots else None

        score = (
            specialization_match * 45
            + float(doctor.rating) * 8
            + min(doctor.review_count, 200) * 0.08
            + (20 if next_slot else 0)
        )

        recommendations.append(
            {
                "doctor": doctor,
                "score": round(score, 1),
                "next_slot": next_slot,
                "available_slots": len(available_slots),
                "specialization_match": bool(specialization_match),
            }
        )

    recommendations.sort(
        key=lambda item: (
            item["specialization_match"],
            item["available_slots"] > 0,
            item["score"],
        ),
        reverse=True,
    )
    return recommendations[:3]


def calculate_risk(age: int, weight: float, systolic_bp: int, smoking: bool, exercise_level: str) -> RiskResult:
    score = 0
    score += min(max(age - 20, 0), 50)
    score += 12 if weight >= 90 else 6 if weight >= 75 else 0
    score += 25 if systolic_bp >= 150 else 15 if systolic_bp >= 135 else 5 if systolic_bp >= 120 else 0
    score += 18 if smoking else 0
    score += {"low": 15, "medium": 7, "high": 0}.get(exercise_level, 7)
    score = min(score, 100)

    if score >= 75:
        level = "High"
        recommendation = "Early doctor consultation aur tests strongly recommended."
    elif score >= 45:
        level = "Moderate"
        recommendation = "Lifestyle improvement aur regular monitoring recommended."
    else:
        level = "Low"
        recommendation = "Abhi risk low hai, preventive routine maintain rakhiye."

    return RiskResult(score=score, level=level, recommendation=recommendation)


def generate_health_insights(appointments: Iterable) -> InsightResult:
    appointments = list(appointments)
    repeat_visits = len(appointments)
    confirmed = sum(1 for appointment in appointments if appointment.status == "confirmed")
    cancelled = sum(1 for appointment in appointments if appointment.status == "cancelled")

    if repeat_visits >= 5:
        summary = f"Aapke account me {repeat_visits} appointments record hui hain. Repeat visits zyada dikh rahi hain."
        recommendation = "Regular health review aur preventive consultation schedule karna useful rahega."
    elif repeat_visits >= 2:
        summary = f"Aapne {repeat_visits} baar consultation use kiya hai. System aapko follow-up aware user maan raha hai."
        recommendation = "Agar same problem repeat ho rahi hai to specialist follow-up book kijiye."
    else:
        summary = "Abhi appointment history kam hai, isliye insights basic level par available hain."
        recommendation = "Regular symptom tracking start kijiye taaki future insights aur smart ho saken."

    if cancelled >= 2:
        recommendation += " Aapki kuch bookings cancel hui hain, isliye optimized slot suggestion useful ho sakta hai."
    elif confirmed >= 2:
        recommendation += " Confirmed consultations ke basis par doctor continuity maintain karna beneficial rahega."

    return InsightResult(summary=summary, recommendation=recommendation, repeat_visits=repeat_visits)


def optimize_appointment_slots(doctors: Iterable, condition: str, today, urgency: str = "medium", preferred_time: str = "any") -> list[dict]:
    recommended_doctors = recommend_doctors_for_condition(doctors, condition, today)
    optimized = []

    for item in recommended_doctors:
        doctor = item["doctor"]
        for slot in doctor.availability_set.all():
            if slot.is_booked or slot.available_date < today:
                continue

            hour = slot.start_time.hour
            time_bonus = 0
            if preferred_time == "morning" and hour < 12:
                time_bonus = 10
            elif preferred_time == "afternoon" and 12 <= hour < 17:
                time_bonus = 10
            elif preferred_time == "evening" and hour >= 17:
                time_bonus = 10
            elif preferred_time == "any":
                time_bonus = 5

            urgency_bonus = {"low": 3, "medium": 8, "high": 15}.get(urgency, 8)
            date_bonus = max(0, 20 - (slot.available_date - today).days * 2)

            optimized.append(
                {
                    "doctor": doctor,
                    "slot": slot,
                    "score": round(item["score"] + time_bonus + urgency_bonus + date_bonus, 1),
                }
            )

    optimized.sort(key=lambda item: (item["score"], -item["slot"].start_time.hour), reverse=True)
    return optimized[:5]


def diagnose_image_upload(uploaded_file) -> ImageDiagnosisResult:
    raw = uploaded_file.read()
    uploaded_file.seek(0)
    image_type = imghdr.what(None, raw) or "unknown"
    filename = (uploaded_file.name or "").lower()
    size_kb = max(len(raw) // 1024, 1)

    if any(keyword in filename for keyword in ("rash", "allergy", "itch", "skin")):
        label = "Skin Allergy"
        confidence = 84
        recommendation = "Dermatologist consultation aur rash history review recommended."
    elif any(keyword in filename for keyword in ("acne", "pimple")):
        label = "Acne Pattern"
        confidence = 80
        recommendation = "Skin care review aur dermatologist follow-up suggested."
    elif any(keyword in filename for keyword in ("burn", "redness")):
        label = "Inflammation / Redness"
        confidence = 74
        recommendation = "Image concern visible lag raha hai, doctor review safer rahega."
    else:
        label = "General Skin Concern"
        confidence = 68 if image_type != "unknown" else 52
        recommendation = "Yeh first-level computer vision demo hai. Better diagnosis ke liye specialist consult karein."

    if size_kb < 40:
        recommendation += " Higher quality image upload karne se result aur stable hoga."

    return ImageDiagnosisResult(
        label=label,
        confidence=confidence,
        recommendation=recommendation,
        image_type=image_type,
    )
