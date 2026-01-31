#!/usr/bin/env python


"""Django's command-line utility for administrative tasks."""
# This is a short docstring (like a comment).
# It describes what this file does: it’s Django’s main entry point for running management commands
# such as running the development server, creating migrations, starting an app, etc.

import os
import sys
# 'os' gives access to operating system features like environment variables.
# 'sys' gives access to system-level variables and arguments (like what command was typed).


def main():
    """Run administrative tasks."""
    # This is the main function that controls the script.
    # It sets up Django's environment and runs whatever command you pass (e.g. runserver, migrate).

    # ------------------------------------------------------------
    # Set an environment variable that tells Django which settings file to use.
    # 'os.environ.setdefault' sets this variable ONLY if it's not already set.
    # The value 'volunteerhub.volunteerhub.settings' refers to the Python path of your settings file:
    #   project_folder/project_name/settings.py
    # This line is critical — Django won’t start without knowing which settings module to load.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "volunteerhub.settings")

    try:
        # Try to import Django’s management utility.
        # 'execute_from_command_line' runs the commands you type after "python manage.py".
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # If Django isn’t installed or can’t be found, this block runs.
        # It raises a clear error message so the user knows what went wrong.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # ------------------------------------------------------------
    # This actually executes the command you typed in the terminal.
    # 'sys.argv' is a list of command-line arguments (like ['manage.py', 'runserver']).
    # So, for example:
    #   python manage.py runserver
    # becomes
    #   execute_from_command_line(['manage.py', 'runserver'])
    # Django reads this and starts the appropriate process (like starting the dev server).
    execute_from_command_line(sys.argv)


# ------------------------------------------------------------
# This part checks if the file is being run directly (not imported as a module).
# '__name__' is a built-in variable:
#   - When you run this file directly, __name__ == '__main__'
#   - When it’s imported, __name__ == the module name (like 'volunteerhub.manage')
# So this ensures the main() function only runs when you call the file directly.
if __name__ == '__main__':
    main()
