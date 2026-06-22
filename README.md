# Doctor Appointment System

A Django-based healthcare appointment and local medicine availability platform for patients, doctors, pharmacies, and administrators. The project demonstrates role-based authentication, doctor discovery, pharmacy stock search, availability management, appointment booking, status updates, dashboards, email notifications, automated tests, and demo AI-assisted healthcare features.

## Best Fit Roles

Use this project for these job profiles:

- Python Developer Intern
- Django Developer Intern
- Backend Developer Intern
- Full Stack Developer Intern, if you explain the Django templates/UI work
- Web Developer Intern with Python/Django focus

Best resume line:

> Built a role-based healthcare platform using Django with patient, doctor, and pharmacy workflows, secure appointment state transitions, pharmacy medicine availability search, PostgreSQL-ready deployment, automated tests, and CI.

## Features

- User registration and login with Django session authentication
- Role-based access for patients, doctors, and pharmacies
- Doctor listing with search, specialization, and availability filters
- Doctor profile and availability slot management
- Appointment booking from available slots
- Patient dashboard with upcoming/history appointments
- Doctor dashboard with appointment request counts
- Appointment approve/reject/cancel status flow
- Pharmacy registration, pharmacy dashboard, and medicine stock management
- Public medicine availability search with location, call, and WhatsApp actions
- Email notifications for booking, status updates, and cancellations
- CSRF-protected POST-only state-changing actions
- Database uniqueness guard to prevent multiple appointments on one slot
- Automated GitHub Actions CI for migrations, Django checks, and tests
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
- SMTP-ready email notifications

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
Pharmacy: demo_pharmacy / demo12345
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

Run the full test suite:

```bash
python core/manage.py test
```

The repository also includes `.github/workflows/ci.yml`, which runs migration checks, Django system checks, and tests on pushes and pull requests to `main`.

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
5. Search `/pharmacies/` for medicine availability and show pharmacy contact actions.
6. Login as a pharmacy and add or update medicine stock.
7. Open the admin panel to show database-backed management.
8. Visit the AI features page to explain future-facing healthcare enhancements.

## Security and Reliability Highlights

- Role-specific dashboard access for patient, doctor, and pharmacy users.
- Appointment approve/reject/cancel and slot delete use POST requests with CSRF protection.
- Booking uses a database transaction and row lock before marking a slot booked.
- A unique database constraint prevents more than one appointment per availability slot.
- Doctors cannot create availability for past dates.
- Tests cover booking, status updates, cancellation, authorization boundaries, POST-only actions, and slot integrity.

## Email Notifications

Local development uses Django's console email backend, so emails print in the terminal. For real emails, set SMTP values in `.env`:

```text
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Doctor Appointment System <your-email@example.com>
```

## Current Limitations

- Payment integration is not implemented.
- The AI modules are demo-oriented and should be expanded with production-grade models before real medical use.
- Pharmacy stock is informational; order placement and payment are future extensions.
