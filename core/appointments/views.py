from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_POST
from django.utils.timezone import localdate
from accounts.models import Patient
from accounts.permissions import role_required
from doctors.models import Doctor, Availability
from .models import Appointment
from .ai_engine import (
    calculate_risk,
    diagnose_image_upload,
    generate_health_insights,
    optimize_appointment_slots,
    predict_from_text,
    recommend_doctors_for_condition,
)


def _send_notification(subject, message, recipients):
    clean_recipients = [email for email in recipients if email]
    if not clean_recipients:
        return

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        clean_recipients,
        fail_silently=True,
    )


def ai_features(request):
    feature_sections = [
        {
            "title": "1. Hybrid Disease Prediction (ML + Rules + Confidence Score)",
            "emoji": "🧠",
            "points": [
                "Sirf disease predict nahi, balki probability aur multiple suggestions.",
                "High confidence aur low confidence cases ke liye alag handling.",
                "RandomForestClassifier + predict_proba() based output.",
            ],
            "output": "Flu - 78%\nCold - 15%\nCovid - 7%",
            "tech": ["RandomForestClassifier", "predict_proba()", "rules + confidence threshold"],
        },
        {
            "title": "2. NLP Symptom Understanding (Chat Input -> Prediction)",
            "emoji": "🤖",
            "points": [
                'User input example: "mujhe 2 din se bukhar aur khansi hai"',
                "Text se symptoms extract karke ML model ko bhejna.",
                "spaCy ya simple keyword parser ke through symptom normalization.",
            ],
            "output": "Extracted symptoms: fever, cough\nPredicted disease: Flu",
            "tech": ["scikit-learn", "spaCy optional", "text preprocessing"],
        },
        {
            "title": "3. Personalized Health Insights",
            "emoji": "📊",
            "points": [
                "User history analyse karke recurring illness patterns detect karna.",
                "Regular checkup aur preventive guidance dena.",
            ],
            "output": 'Aapko last 3 months me 5 baar fever hua\nRegular checkup recommended',
            "tech": ["pandas", "history aggregation", "pattern detection"],
        },
        {
            "title": "4. Risk Prediction System",
            "emoji": "🫀",
            "points": [
                "Age, weight, BP, habits jaise inputs se health risk score nikalna.",
                "Doctor ko preventive consultation ke liye recommend karna.",
            ],
            "output": "Heart Disease Risk: 82%",
            "tech": ["Logistic Regression", "Random Forest", "risk scoring"],
        },
        {
            "title": "5. Smart Doctor Recommendation",
            "emoji": "🩺",
            "points": [
                "Specialization ke saath rating, distance, availability aur success rate score.",
                "Disease/symptom ke hisaab se best doctor ranking.",
            ],
            "output": "Recommended: Gynecologist -> Dr Doctor One",
            "tech": ["weighted scoring", "specialization mapping", "availability boost"],
        },
        {
            "title": "6. AI Appointment Optimization",
            "emoji": "📅",
            "points": [
                "Best slot suggest karna based on busy hours aur patient urgency.",
                "Doctor calendar ko intelligently utilize karna.",
            ],
            "output": "Suggested slot: 2026-04-20 | 10:00 - 11:00",
            "tech": ["slot scoring", "queue reduction logic", "priority rules"],
        },
        {
            "title": "7. Computer Vision Diagnosis",
            "emoji": "📷",
            "points": [
                "Skin image upload karke disease detect karne ka future-ready module.",
                "CNN/TensorFlow based diagnosis pipeline ka placeholder.",
            ],
            "output": "Potential diagnosis: Skin Allergy",
            "tech": ["CNN", "TensorFlow", "image preprocessing"],
        },
    ]

    code_samples = {
        "dataset.csv": "fever,cough,headache,fatigue,disease\n1,1,1,1,Flu\n1,1,0,1,Cold\n0,1,1,0,Allergy\n1,0,1,1,Dengue\n0,0,1,1,Migraine",
        "train_model.py": "import pandas as pd\nfrom sklearn.ensemble import RandomForestClassifier\nimport pickle\n\n\ndf = pd.read_csv('dataset.csv')\nX = df.drop('disease', axis=1)\ny = df['disease']\n\nmodel = RandomForestClassifier()\nmodel.fit(X, y)\n\npickle.dump(model, open('model.pkl', 'wb'))\nprint('Model trained & saved!')",
        "appointments_ml_model.py": "import pickle\n\nmodel = pickle.load(open('model.pkl', 'rb'))\n\n\ndef predict_disease(data):\n    prediction = model.predict([data])[0]\n    probs = model.predict_proba([data])[0]\n    return prediction, max(probs)",
    }

    symptom_result = None
    risk_result = None
    insights_result = None
    optimized_slots = []
    image_result = None
    symptom_text = ""
    risk_inputs = {
        "age": "",
        "weight": "",
        "systolic_bp": "",
        "smoking": "no",
        "exercise_level": "medium",
    }
    optimization_inputs = {
        "condition": "",
        "urgency": "medium",
        "preferred_time": "any",
    }

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "symptom_prediction":
            symptom_text = request.POST.get("symptom_text", "").strip()
            if symptom_text:
                symptom_result = predict_from_text(symptom_text)
                doctors = Doctor.objects.prefetch_related("availability_set").all()
                symptom_result["recommended_doctors"] = recommend_doctors_for_condition(
                    doctors,
                    symptom_result["primary_condition"],
                    localdate(),
                )
            else:
                messages.error(request, "Please enter symptoms before prediction.")

        elif form_type == "risk_prediction":
            risk_inputs = {
                "age": request.POST.get("age", "").strip(),
                "weight": request.POST.get("weight", "").strip(),
                "systolic_bp": request.POST.get("systolic_bp", "").strip(),
                "smoking": request.POST.get("smoking", "no"),
                "exercise_level": request.POST.get("exercise_level", "medium"),
            }
            if all(risk_inputs[key] for key in ("age", "weight", "systolic_bp")):
                risk_result = calculate_risk(
                    age=int(risk_inputs["age"]),
                    weight=float(risk_inputs["weight"]),
                    systolic_bp=int(risk_inputs["systolic_bp"]),
                    smoking=risk_inputs["smoking"] == "yes",
                    exercise_level=risk_inputs["exercise_level"],
                )
            else:
                messages.error(request, "Please fill all risk input fields.")

        elif form_type == "personalized_insights":
            if request.user.is_authenticated and Patient.objects.filter(user=request.user).exists():
                patient = Patient.objects.get(user=request.user)
                appointments = Appointment.objects.filter(patient=patient).select_related("doctor", "availability")
                insights_result = generate_health_insights(appointments)
            else:
                demo_appointments = Appointment.objects.all()[:3]
                insights_result = generate_health_insights(demo_appointments)

        elif form_type == "appointment_optimization":
            optimization_inputs = {
                "condition": request.POST.get("condition", "").strip(),
                "urgency": request.POST.get("urgency", "medium"),
                "preferred_time": request.POST.get("preferred_time", "any"),
            }
            condition = optimization_inputs["condition"] or "Flu"
            doctors = Doctor.objects.prefetch_related("availability_set").all()
            optimized_slots = optimize_appointment_slots(
                doctors,
                condition=condition,
                today=localdate(),
                urgency=optimization_inputs["urgency"],
                preferred_time=optimization_inputs["preferred_time"],
            )

        elif form_type == "image_diagnosis":
            uploaded = request.FILES.get("skin_image")
            if uploaded:
                image_result = diagnose_image_upload(uploaded)
            else:
                messages.error(request, "Please upload an image for diagnosis.")

    return render(
        request,
        "ai_features.html",
        {
            "feature_sections": feature_sections,
            "code_samples": code_samples,
            "symptom_result": symptom_result,
            "risk_result": risk_result,
            "insights_result": insights_result,
            "optimized_slots": optimized_slots,
            "image_result": image_result,
            "symptom_text": symptom_text,
            "risk_inputs": risk_inputs,
            "optimization_inputs": optimization_inputs,
        },
    )


@login_required
@role_required("patient", redirect_url="/doctor-dashboard/")
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id, is_verified=True)
    patient = get_object_or_404(Patient, user=request.user)

    # Sirf unbooked slots hi dikhayein.
    slots = Availability.objects.filter(doctor=doctor, is_booked=False).order_by(
        "available_date", "start_time"
    )

    if request.method == "POST":
        slot_id = request.POST.get("slot_id")

        try:
            with transaction.atomic():
                slot = get_object_or_404(
                    Availability.objects.select_for_update(),
                    id=slot_id,
                    doctor=doctor,
                    is_booked=False,
                    available_date__gte=localdate(),
                )

                appointment = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    availability=slot,
                    appointment_date=slot.available_date,
                )
                slot.is_booked = True
                slot.save(update_fields=["is_booked"])
        except IntegrityError:
            messages.error(request, "This slot was just booked. Please choose another slot.")
            return redirect("book_appointment", doctor_id=doctor.id)


        messages.success(request, "Appointment booked successfully.")
        _send_notification(
            "Appointment booking received",
            (
                f"Your appointment request with {doctor.name or doctor.user.username} "
                f"for {appointment.appointment_date} at {slot.start_time} is pending confirmation."
            ),
            [patient.user.email],
        )
        _send_notification(
            "New appointment request",
            (
                f"{patient.patient_name} booked an appointment for {appointment.appointment_date} "
                f"at {slot.start_time}. Please approve or reject it from your dashboard."
            ),
            [doctor.email_id, doctor.user.email],
        )

        return redirect('patient_dashboard')

    return render(request, "book.html", {
        "doctor": doctor,
        "slots": slots
    })


@login_required
@role_required("doctor", redirect_url="/login/")
@require_POST
def update_status(request, id, status):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=id, doctor=doctor)

    status_map = {
        "approved": "confirmed",
        "rejected": "cancelled",
        "confirmed": "confirmed",
        "cancelled": "cancelled",
    }
    normalized_status = status_map.get(status.lower())

    if normalized_status is None:
        messages.error(request, "Invalid appointment status.")
        return redirect("doctor_dashboard")

    appointment.status = normalized_status
    appointment.save(update_fields=["status"])
    appointment.availability.is_booked = normalized_status != "cancelled"
    appointment.availability.save(update_fields=["is_booked"])

    messages.success(
        request,
        f"Appointment for {appointment.patient.patient_name} marked as {appointment.get_status_display()}.",
    )
    _send_notification(
        f"Appointment {appointment.get_status_display()}",
        (
            f"Your appointment with {appointment.doctor.name or appointment.doctor.user.username} "
            f"on {appointment.appointment_date} has been marked as {appointment.get_status_display()}."
        ),
        [appointment.patient.user.email],
    )
    return redirect("doctor_dashboard")


@login_required
@role_required("patient", redirect_url="/login/")
@require_POST
def cancel_appointment(request, id):
    patient = get_object_or_404(Patient, user=request.user)
    appointment = get_object_or_404(Appointment, id=id, patient=patient)

    appointment.status = "cancelled"
    appointment.save(update_fields=["status"])
    appointment.availability.is_booked = False
    appointment.availability.save(update_fields=["is_booked"])

    messages.success(request, "Appointment cancelled successfully.")
    _send_notification(
        "Appointment cancelled",
        (
            f"{patient.patient_name} cancelled the appointment scheduled on "
            f"{appointment.appointment_date}."
        ),
        [appointment.doctor.email_id, appointment.doctor.user.email],
    )
    return redirect("patient_dashboard")
