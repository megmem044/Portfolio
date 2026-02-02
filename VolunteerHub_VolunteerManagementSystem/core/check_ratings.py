#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volunteerhub.settings')
django.setup()

from signups.models_event import Event, EventRating
from signups.models import Volunteer

# Find Chess event
chess_event = Event.objects.filter(name__icontains='chess').first()
print(f"Chess event ID: {chess_event.id if chess_event else 'Not found'}")

# Find Lee volunteer
lee = Volunteer.objects.filter(name='Lee').first()
print(f"Lee volunteer ID: {lee.id if lee else 'Not found'}")

# Check for ratings
if chess_event:
    ratings = EventRating.objects.filter(event=chess_event)
    print(f"\nTotal ratings for {chess_event.name}: {ratings.count()}")
    for r in ratings:
        print(f"  - {r.volunteer.name}: {r.rating}/5 - {r.comment}")
