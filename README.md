# Doctor Appointment System

A Django-based healthcare appointment booking system for patients, doctors, and administrators. The project demonstrates role-based authentication, doctor discovery, availability management, appointment booking, status updates, dashboards, and demo AI-assisted healthcare features.

## Best Fit Roles

Use this project for these job profiles:

- Python Developer Intern
- Django Developer Intern
- Backend Developer Intern
- Full Stack Developer Intern, if you explain the Django templates/UI work
- Web Developer Intern with Python/Django focus

Best resume line:

> Built a role-based Doctor Appointment System using Django, SQLite/PostgreSQL-ready configuration, session authentication, patient and doctor dashboards, appointment booking workflow, and AI-assisted health feature demos.

## Features

- User registration and login with Django session authentication
- Role-based access for patients and doctors
- Doctor listing with search, specialization, and availability filters
- Doctor profile and availability slot management
- Appointment booking from available slots
- Patient dashboard with upcoming/history appointments
- Doctor dashboard with appointment request counts
- Appointment approve/reject/cancel status flow
- Django admin panel for managing users, doctors, slots, and appointments
- Demo data seeding command for recruiter walkthroughs
- AI feature page for symptom prediction, risk scoring, doctor recommendation, appointment optimization, and image diagnosis demo flows

## Tech Stack

- Python
- Django 5.2
- SQLite for local development
- PostgreSQL-ready deployment through `DATABASE_URL`
- HTML, CSS, Django templates
- Gunicorn for production serving

## Database

Local development uses SQLite by default.

Production deployment can use PostgreSQL by setting `DATABASE_URL`.

## Authentication

Authentication uses Django's built-in auth system with session-based login. The project uses `authenticate()`, `login()`, `logout()`, and `@login_required`.

## Local Setup

```bash
git clone https://github.com/Satishsrivastav045/Doctor_Appointment_System.git
cd Doctor_Appointment_System
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python core/manage.py migrate
python core/manage.py seed_demo
python core/manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Demo logins:

```text
Patient: demo_patient / demo12345
Doctor: demo_dr_neha / demo12345
```

## Admin Panel

Create a superuser:

```bash
python core/manage.py createsuperuser
```

Admin URL:

```text
http://127.0.0.1:8000/admin/
```

## Tests

Run the appointment workflow tests:

```bash
python core/manage.py test appointments
```

## Render Deployment

The repository includes `render.yaml` and `Procfile`.

For Render:

- Create a new Blueprint from this GitHub repo, or create a Web Service manually.
- Use PostgreSQL and set `DATABASE_URL`.
- Set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.
- Build command:

```bash
pip install -r requirements.txt && python core/manage.py collectstatic --noinput && python core/manage.py migrate && python core/manage.py seed_demo
```

- Start command:

```bash
gunicorn core.wsgi:application --chdir core
```

## Recruiter Walkthrough

1. Register as a patient and view available doctors.
2. Book an appointment from an available doctor slot.
3. Login as a doctor and approve or reject the appointment.
4. Open the patient dashboard to verify the status update.
5. Open the admin panel to show database-backed management.
6. Visit the AI features page to explain future-facing healthcare enhancements.

## Current Limitations

- Email notification is not implemented yet.
- Payment integration is not implemented.
- The AI modules are demo-oriented and should be expanded with production-grade models before real medical use.
