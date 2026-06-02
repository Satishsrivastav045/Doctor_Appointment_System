from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localdate
from .models import Availability, Doctor


def _get_available_slots(doctor, today):
    available_slots = [
        slot for slot in doctor.availability_set.all()
        if not slot.is_booked and slot.available_date >= today
    ]
    available_slots.sort(key=lambda slot: (slot.available_date, slot.start_time))
    return available_slots


def doctor_list(request):
    query = request.GET.get("q", "").strip()
    availability_filter = request.GET.get("availability", "").strip()
    specialization_filter = request.GET.get("specialization", "").strip()

    doctors = Doctor.objects.prefetch_related("availability_set").order_by("name", "user__username")
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query)
            | Q(specialization__icontains=query)
            | Q(user__username__icontains=query)
        )
    if specialization_filter:
        doctors = doctors.filter(specialization__iexact=specialization_filter)

    doctor_cards = []
    today = localdate()

    for doctor in doctors:
        available_slots = _get_available_slots(doctor, today)
        next_slot = available_slots[0] if available_slots else None
        if availability_filter == "open" and not available_slots:
            continue

        doctor_cards.append(
            {
                "doctor": doctor,
                "available_slots": len(available_slots),
                "next_slot": next_slot,
            }
        )

    return render(
        request,
        "doctor_list.html",
        {
            "doctor_cards": doctor_cards,
            "doctor_count": len(doctor_cards),
            "search_query": query,
            "availability_filter": availability_filter,
            "specialization_filter": specialization_filter,
            "specializations": [
                item for item in Doctor.objects.exclude(specialization="").values_list("specialization", flat=True).distinct().order_by("specialization")
            ],
        },
    )


def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor.objects.prefetch_related("availability_set"), id=doctor_id)
    today = localdate()
    available_slots = _get_available_slots(doctor, today)

    return render(
        request,
        "doctor_detail.html",
        {
            "doctor": doctor,
            "next_slot": available_slots[0] if available_slots else None,
            "available_slots": available_slots[:6],
            "available_slot_count": len(available_slots),
        },
    )


@login_required
def manage_availability(request):
    if not Doctor.objects.filter(user=request.user).exists():
        messages.error(request, "Only doctors can manage availability.")
        return redirect("/login/")

    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == "POST":
        form_type = request.POST.get("form_type", "slot")

        if form_type == "profile":
            doctor.name = request.POST.get("name", "").strip()
            doctor.specialization = request.POST.get("specialization", "").strip()
            doctor.email_id = request.POST.get("email_id", "").strip()
            doctor.phone_no = request.POST.get("phone_no", "").strip()
            doctor.photo_url = request.POST.get("photo_url", "").strip()
            doctor.whatsapp_number = request.POST.get("whatsapp_number", "").strip()
            doctor.consultation_fee = request.POST.get("consultation_fee") or 0
            doctor.rating = request.POST.get("rating") or 4.5
            doctor.review_count = request.POST.get("review_count") or 0
            doctor.save(
                update_fields=[
                    "name",
                    "specialization",
                    "email_id",
                    "phone_no",
                    "photo_url",
                    "whatsapp_number",
                    "consultation_fee",
                    "rating",
                    "review_count",
                ]
            )
            messages.success(request, "Doctor profile updated successfully.")
            return redirect("manage_availability")

        available_date = request.POST.get("available_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not available_date or not start_time or not end_time:
            messages.error(request, "Date, start time, and end time are required.")
            return redirect("manage_availability")

        start_obj = datetime.strptime(start_time, "%H:%M").time()
        end_obj = datetime.strptime(end_time, "%H:%M").time()

        if end_obj <= start_obj:
            messages.error(request, "End time must be later than start time.")
            return redirect("manage_availability")

        if Availability.objects.filter(
            doctor=doctor,
            available_date=available_date,
            start_time=start_obj,
            end_time=end_obj,
        ).exists():
            messages.error(request, "This slot already exists.")
            return redirect("manage_availability")

        Availability.objects.create(
            doctor=doctor,
            available_date=available_date,
            start_time=start_obj,
            end_time=end_obj,
        )
        messages.success(request, "Availability slot added successfully.")
        return redirect("manage_availability")

    slots = Availability.objects.filter(doctor=doctor).order_by("available_date", "start_time")
    return render(
        request,
        "manage_availability.html",
        {
            "doctor": doctor,
            "slots": slots,
            "slot_count": slots.count(),
            "open_count": slots.filter(is_booked=False).count(),
            "booked_count": slots.filter(is_booked=True).count(),
        },
    )


@login_required
def edit_availability(request, slot_id):
    if not Doctor.objects.filter(user=request.user).exists():
        messages.error(request, "Only doctors can edit availability.")
        return redirect("/login/")

    doctor = get_object_or_404(Doctor, user=request.user)
    slot = get_object_or_404(Availability, id=slot_id, doctor=doctor)

    if slot.is_booked:
        messages.error(request, "Booked slots cannot be edited.")
        return redirect("manage_availability")

    if request.method == "POST":
        available_date = request.POST.get("available_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not available_date or not start_time or not end_time:
            messages.error(request, "Date, start time, and end time are required.")
            return redirect("edit_availability", slot_id=slot.id)

        start_obj = datetime.strptime(start_time, "%H:%M").time()
        end_obj = datetime.strptime(end_time, "%H:%M").time()

        if end_obj <= start_obj:
            messages.error(request, "End time must be later than start time.")
            return redirect("edit_availability", slot_id=slot.id)

        duplicate = Availability.objects.filter(
            doctor=doctor,
            available_date=available_date,
            start_time=start_obj,
            end_time=end_obj,
        ).exclude(id=slot.id)
        if duplicate.exists():
            messages.error(request, "Another slot already exists for this time.")
            return redirect("edit_availability", slot_id=slot.id)

        slot.available_date = available_date
        slot.start_time = start_obj
        slot.end_time = end_obj
        slot.save(update_fields=["available_date", "start_time", "end_time"])
        messages.success(request, "Slot updated successfully.")
        return redirect("manage_availability")

    return render(
        request,
        "edit_availability.html",
        {
            "doctor": doctor,
            "slot": slot,
        },
    )


@login_required
def delete_availability(request, slot_id):
    if not Doctor.objects.filter(user=request.user).exists():
        messages.error(request, "Only doctors can delete availability.")
        return redirect("/login/")

    doctor = get_object_or_404(Doctor, user=request.user)
    slot = get_object_or_404(Availability, id=slot_id, doctor=doctor)

    if slot.is_booked:
        messages.error(request, "Booked slots cannot be deleted.")
        return redirect("manage_availability")

    slot.delete()
    messages.success(request, "Slot deleted successfully.")
    return redirect("manage_availability")
