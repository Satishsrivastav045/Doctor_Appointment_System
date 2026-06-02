from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localdate
from .models import User, Role, Patient
from appointments.models import Appointment
from doctors.models import Doctor


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob') or None
        role_id = request.POST.get('role')

        # Validation
        if not username or not password or not role_id:
            messages.error(request, "All fields are required!")
            return redirect('/register/')

        # Check duplicate user
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('/register/')

        role = Role.objects.get(id=role_id)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=full_name,
            role=role
        )

        if role.role_name == 'doctor':
            Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'name': full_name or username,
                    'email_id': email or '',
                    'hospital_name': request.POST.get('hospital_name', '').strip(),
                    'specialization': request.POST.get('specialization', '').strip(),
                    'phone_no': request.POST.get('phone_no', '').strip(),
                    'whatsapp_number': request.POST.get('whatsapp_number', '').strip(),
                    'district': request.POST.get('district', '').strip(),
                    'city_or_block': request.POST.get('city_or_block', '').strip(),
                    'village_or_area': request.POST.get('village_or_area', '').strip(),
                    'full_address': request.POST.get('full_address', '').strip(),
                    'latitude': request.POST.get('latitude') or None,
                    'longitude': request.POST.get('longitude') or None,
                    'consultation_mode': request.POST.get('consultation_mode') or 'offline',
                    'is_emergency_available': request.POST.get('is_emergency_available') == 'on',
                }
            )
        else:
            Patient.objects.get_or_create(
                user=user,
                defaults={
                    'patient_name': full_name or username,
                    'dob': dob,
                }
            )

        login(request, user)

        # Role-based redirect
        if role.role_name == 'doctor':
            return redirect('/doctor-dashboard/')
        else:
            return redirect('/patient-dashboard/')

    roles = Role.objects.all()
    return render(request, 'register.html', {'roles': roles})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Role-based redirect
            if user.role and user.role.role_name == 'doctor':
                return redirect('/doctor-dashboard/')
            else:
                return redirect('/patient-dashboard/')
        else:
            messages.error(request, "Invalid username or password!")

    # ⭐ VERY IMPORTANT (error fix)
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('/login/')


@login_required
def patient_dashboard(request):
    if not Patient.objects.filter(user=request.user).exists():
        messages.error(request, "You are not allowed to open the patient dashboard.")
        return redirect('/doctor-dashboard/')

    patient = get_object_or_404(Patient, user=request.user)
    appointments = list(Appointment.objects.filter(patient=patient).select_related(
        'doctor', 'availability'
    ))
    today = localdate()
    upcoming_appointments = []
    history_appointments = []

    for appointment in appointments:
        if appointment.status != "cancelled" and appointment.appointment_date >= today:
            upcoming_appointments.append(appointment)
        else:
            history_appointments.append(appointment)

    active_tab = request.GET.get("tab", "upcoming")
    if active_tab not in {"upcoming", "history"}:
        active_tab = "upcoming"

    return render(
        request,
        'patient_dashboard.html',
        {
            'appointments': appointments,
            'upcoming_appointments': upcoming_appointments,
            'history_appointments': history_appointments,
            'active_tab': active_tab,
            'patient_stats': {
                'total': len(appointments),
                'upcoming': len(upcoming_appointments),
                'history': len(history_appointments),
            },
        }
    )


@login_required
def doctor_dashboard(request):
    if not Doctor.objects.filter(user=request.user).exists():
        messages.error(request, "You are not allowed to open the doctor dashboard.")
        return redirect('/patient-dashboard/')

    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = list(Appointment.objects.filter(doctor=doctor).select_related(
        'patient', 'availability'
    ))
    pending_count = sum(1 for appointment in appointments if appointment.status == "pending")
    confirmed_count = sum(1 for appointment in appointments if appointment.status == "confirmed")
    cancelled_count = sum(1 for appointment in appointments if appointment.status == "cancelled")

    return render(
        request,
        'doctor_dashboard.html',
        {
            'appointments': appointments,
            'doctor_stats': {
                'total': len(appointments),
                'pending': pending_count,
                'confirmed': confirmed_count,
                'cancelled': cancelled_count,
            },
        }
    )
