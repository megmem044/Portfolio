# VolunteerHub

**Last updated:** August 15, 2026

VolunteerHub is becoming a multi-organization platform for running volunteer
programs. It is meant for small nonprofits, student groups, community
associations, and event organizers that need one place to schedule volunteers,
check attendance, confirm qualifications, and track service hours.

The project started as a working volunteer tracking prototype. It is now being
independently redesigned around the needs of real organizations and volunteers.
The goal is to turn it into a product that can be deployed, used, and improved
through direct user feedback.

## Product direction

Each organization will have its own coordinators, volunteers, events,
certificates, attendance records, hours, and reports. A person may volunteer for
one organization and coordinate for another.

The main workflows will be:

- Volunteers find an event, check its requirements, choose a role and shift,
  register, receive reminders, check in and out, and receive verified hours.
- Coordinators create events, set roles and shift capacity, review volunteers,
  manage attendance, verify hours, and create reports.
- Organization administrators manage coordinators, organization settings,
  certifications, records, and organization-wide reports.

The planned product also includes waitlists, schedule conflict checks,
qualification rules, QR check-in and check-out, email reminders, calendar
downloads, audit history, and data exports.

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the planned work and delivery order.

## Current state

The existing application already provides a foundation for opportunities,
events, roles, shifts, signups, volunteer hours, and certificate review. The
next stage is to place these features inside organization accounts and connect
them into complete day-to-day workflows.

The application uses Django, Django REST Framework, Django templates, and small
JavaScript enhancements. SQLite is used for local development. PostgreSQL is
planned for production. The project will stay server-rendered instead of being
rewritten as a single-page application.

## Running the project locally

Python 3.8 or newer is required. From this directory, create a virtual
environment and install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set up the database and start the server:

```powershell
python manage.py migrate
python manage.py runserver
```

For a deployed copy, set `DJANGO_SECRET_KEY` to a private, randomly generated
value. The fallback value in `settings.py` is intended only for local work.

The site will be available at <http://127.0.0.1:8000/>. The Django admin is at
<http://127.0.0.1:8000/admin/>. To use the admin, create an account first:

```powershell
python manage.py createsuperuser
```

Uploaded certificates and images are saved in `media/`. The SQLite database and
uploaded files are ignored by Git, so each local setup starts without shared
user data.

## Main folders

- `volunteerhub/` contains the Django settings and main URL configuration.
- `signups/` contains the models, views, API serializers, routes, migrations,
  and page templates.
- `templates/` contains templates shared across the project.
- `scripts/` contains small maintenance and debugging scripts.
- `docs/` contains the implementation notes, source guide, and test results.

The complete walkthrough and manual test cases are in
[`docs/SETUP_AND_TESTING.md`](docs/SETUP_AND_TESTING.md).
