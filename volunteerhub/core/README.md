# VolunteerHub

VolunteerHub is a volunteer tracking and matching system built for CMPT 370 by
Team 9. It gives coordinators a place to post opportunities, create events and
shifts, review signups, and track certificates. Volunteers can browse available
work, manage their schedule, record completed hours, and keep a small portfolio.

The project uses Django and Django REST Framework. Pages are rendered with
Django templates, and development data is stored in SQLite.

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
