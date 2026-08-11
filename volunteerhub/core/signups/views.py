# File: signups/views.py
# Purpose:
#   Handles all HTML pages and all API viewsets.
#   View names match the URL patterns exactly to avoid errors.

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from .models import (
    Volunteer,
    Coordinator,
    Role,
    Enrollment,
    Certificate,
    CulturalInterest,
    Post,
    VolunteerWorkPhoto,
)

from .serializers import (
    VolunteerSerializer,
    CoordinatorSerializer,
    RoleSerializer,
    EnrollmentSerializer,
    CertificateSerializer,
    CulturalInterestSerializer,
    PostSerializer,
    VolunteerWorkPhotoSerializer,
)


# -----------------------------------------------------
# HTML PAGES
# -----------------------------------------------------

# Landing page with choice between volunteer and coordinator signup
def landing_page(request):
    return render(request, "signups/landingPage.html")

# Landing page for signup/signin
def signup_landing_page(request):
    # Show signup/signin page first
    return render(request, "signups/volunteerSignup.html")

# Coordinator signup page
def coordinator_signup_page(request):
    return render(request, "signups/coordinatorSignup.html")

# Student volunteer signup page  
def volunteer_signup_page(request):
    return render(request, "signups/volunteerSignup.html")

@login_required(login_url="/volunteer-signup/")
def home_page(request):
    return render(request, "signups/home.html")


# Volunteer list page
def volunteer_list_page(request):
    return render(request, "signups/volunteer_list.html")


# Certificate upload page
def certificate_upload_page(request):
    return render(request, "signups/certificateUpload.html")


# EmiExplorer preferences page
def emi_preferences_page(request):
    return render(request, "signups/preferences.html")


# Posts list page
def posts_list_page(request):
    return render(request, "signups/posts_list.html")


# Create post page
# This was corrected to match the URL pattern
def create_post_page(request):
    return render(request, "signups/create_post.html")


# Edit post page
def edit_post_page(request):
    return render(request, "signups/edit_post.html")


# Coordinator dashboard page
def coordinator_dashboard_page(request):
    # Check if coordinator is logged in
    if not request.session.get('coordinator_email'):
        return redirect('coordinator-signin')
    return render(request, "coordinator/coordinator_dashboard.html")

def coordinator_profile_page(request):
    # Check if coordinator is logged in
    if not request.session.get('coordinator_email'):
        return redirect('coordinator-signin')
    return render(request, "coordinator/coordinator_profile.html")

# Role creation page
def role_create_page(request):
    return render(request, "signups/role_create.html")

# Volunteer profile page
def volunteer_profile_page(request, volunteer_id):
    return render(request, "volunteer/volunteer_profile.html", {"volunteer_id": volunteer_id})

# Volunteer dashboard page
def volunteer_dashboard_page(request):
    # Check if volunteer is logged in
    if not request.user.is_authenticated:
        return redirect('volunteer-signin')
    return render(request, "volunteer/volunteer_home.html")

# Volunteer profile page (without ID)
def volunteer_profile_page_simple(request):
    # Check if volunteer is logged in
    if not request.user.is_authenticated:
        return redirect('volunteer-signin')
    
    # Get the logged-in user's volunteer record
    # Use filter().first() to handle potential duplicates gracefully
    volunteer = Volunteer.objects.filter(email=request.user.email).first()
    if volunteer:
        return render(request, "volunteer/volunteer_profile.html", {"volunteer_id": volunteer.id})
    # If no volunteer found by email, still render the page - JavaScript will handle missing data
    return render(request, "volunteer/volunteer_profile.html")

# Volunteer signin page
def volunteer_signin_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Find user by email
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            # Authenticate with username (Django's default auth uses username)
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                auth_login(request, authenticated_user)
                return redirect("/volunteer/home/")
            else:
                return render(request, "volunteer/volunteer_signin.html", {"error": "Invalid password"})
        except User.DoesNotExist:
            return render(request, "volunteer/volunteer_signin.html", {"error": "Email not found"})
    
    return render(request, "volunteer/volunteer_signin.html")

# Logout view for both volunteers and coordinators
def logout_view(request):
    """Handle logout for both volunteers and coordinators"""
    if request.method == "POST":
        # Logout Django user (for volunteers)
        auth_logout(request)
        
        # Also clear coordinator session if it exists
        if 'coordinator_email' in request.session:
            del request.session['coordinator_email']
        if 'coordinator_id' in request.session:
            del request.session['coordinator_id']
        
        request.session.save()
        
        # Redirect to volunteer signin
        return redirect("/volunteer/signin/")
    
    # If GET request, just redirect (for backwards compatibility)
    auth_logout(request)
    if 'coordinator_email' in request.session:
        del request.session['coordinator_email']
    if 'coordinator_id' in request.session:
        del request.session['coordinator_id']
    return redirect("/volunteer/signin/")

# Coordinator signin page
def coordinator_signin_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Find user by email
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            # Authenticate with username
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                auth_login(request, authenticated_user)
                # Store coordinator email in session for event creation
                request.session['coordinator_email'] = email
                return redirect("coordinator-dashboard")
            else:
                return render(request, "coordinator/coordinator_signin.html", {"error": "Invalid password"})
        except User.DoesNotExist:
            return render(request, "coordinator/coordinator_signin.html", {"error": "Email not found"})
    
    return render(request, "coordinator/coordinator_signin.html")

# Volunteer opportunities page
def volunteer_opportunities_page(request):
    # Check if volunteer is logged in
    if not request.user.is_authenticated:
        return redirect('volunteer-signin')
    return render(request, "volunteer/volunteer_opportunities.html")

# Volunteer schedule page
def volunteer_schedule_page(request):
    # Check if volunteer is logged in
    if not request.user.is_authenticated:
        return redirect('volunteer-signin')
    return render(request, "volunteer/volunteer_schedule.html")

# Volunteer certificates page
def volunteer_certificates_page(request):
    # Check if volunteer is logged in
    if not request.user.is_authenticated:
        return redirect('volunteer-signin')
    return render(request, "volunteer/volunteer_certificates.html")

# Volunteer event rating page
def volunteer_event_rating_page(request):
    # Check if volunteer is logged in
    if not request.user.is_authenticated:
        return redirect('volunteer-signin')
    return render(request, "volunteer/volunteer_event_rating.html")

# Volunteer photos page
def volunteer_photos_page(request):
    return render(request, "volunteer/volunteer_photos.html")


# Coordinator event list page
def coordinator_event_list_page(request):
    from .models_event import Event
    
    coordinator_id = request.session.get('coordinator_id')
    
    # Get all events (or filter by coordinator if needed)
    if coordinator_id:
        events = Event.objects.filter(coordinator_id=coordinator_id).order_by('-created_at')
    else:
        events = Event.objects.all().order_by('-created_at')
    
    return render(request, "coordinator/coordinator_event_list.html", {
        "events": events
    })

# Coordinator event create page
def coordinator_event_create_page(request):
    if request.method == "POST":
        from django.utils import timezone
        from datetime import datetime
        from .models_event import Event
        from .models import Coordinator
        
        # Get form data
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location')
        max_volunteers = request.POST.get('max_volunteers')
        description = request.POST.get('description')
        notes = request.POST.get('notes')
        requires_first_aid = request.POST.get('requires_first_aid') == 'on'
        requires_food_safety = request.POST.get('requires_food_safety') == 'on'
        
        try:
            # Parse dates and times
            start_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
            
            # Make timezone-aware
            start_dt = timezone.make_aware(start_dt)
            end_dt = timezone.make_aware(end_dt)
            
            # Get the coordinator from session
            coordinator_email = request.session.get('coordinator_email')
            coordinator = Coordinator.objects.filter(email=coordinator_email).first() if coordinator_email else None
            
            # Create event
            event = Event.objects.create(
                name=name,
                start_datetime=start_dt,
                end_datetime=end_dt,
                location=location,
                max_volunteers=int(max_volunteers),
                description=description or "",
                notes=notes or "",
                requires_first_aid=requires_first_aid,
                requires_food_safety=requires_food_safety,
                coordinator=coordinator
            )
            
            # Redirect to event list
            from django.shortcuts import redirect
            return redirect('/coordinator/events/')
            
        except Exception as e:
            # If error, re-render form with error message
            return render(request, "coordinator/coordinator_event_create.html", {
                "error": f"Error creating event: {str(e)}"
            })
    
    return render(request, "coordinator/coordinator_event_create.html")

# Coordinator event edit page
def coordinator_event_edit_page(request, event_id):
    return render(request, "coordinator/coordinator_event_edit.html", {"event_id": event_id})

def coordinator_event_manage_page(request, event_id):
    # Check if coordinator is logged in
    if not request.session.get('coordinator_email'):
        return redirect('coordinator-signin')
    return render(request, "coordinator/coordinator_event_manage.html", {"event_id": event_id})

def coordinator_event_signups_page(request, event_id):
    # Check if coordinator is logged in
    if not request.session.get('coordinator_email'):
        return redirect('coordinator-signin')
    return render(request, "coordinator/coordinator_event_signups.html", {"event_id": event_id})

# Coordinator event delete page
def coordinator_event_delete_page(request, event_id):
    from .models_event import Event
    from django.shortcuts import redirect
    
    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        # Redirect back to event list after deletion
        return redirect('/coordinator/events/')
    except Event.DoesNotExist:
        # If event doesn't exist, redirect to event list
        return redirect('/coordinator/events/')

# Coordinator event dashboard page
def coordinator_event_dashboard_page(request, event_id):
    return render(request, "coordinator/coordinator_event_dashboard.html", {"event_id": event_id})

# Coordinator event details page
def coordinator_event_details_page(request, event_id):
    return render(request, "coordinator/coordinator_event_details.html", {"event_id": event_id})

# Coordinator event schedule page
def coordinator_event_schedule_page(request, event_id):
    return render(request, "coordinator/coordinator_event_schedule.html", {"event_id": event_id})

# Coordinator event feedback page
def coordinator_event_feedback_page(request, event_id):
    from .models_event import Event
    
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        event = None
    
    return render(request, "coordinator/coordinator_event_feedback.html", {"event": event, "event_id": event_id})

# Coordinator event ratings page
def coordinator_event_ratings_page(request, event_id):
    return render(request, "coordinator/coordinator_event_ratings.html", {"event_id": event_id})

# Coordinator shift assignment page
def coordinator_shift_assignment_page(request, event_id):
    return render(request, "coordinator/coordinator_shift_assignment.html", {"event_id": event_id})

# Coordinator volunteer signups page
def coordinator_volunteer_signups_page(request):
    return render(request, "coordinator/coordinator_volunteer_signups.html")

# Coordinator shifts list page - shows all events to select which to manage shifts for
def coordinator_shifts_list_page(request):
    from .models_event import Event
    
    coordinator_id = request.session.get('coordinator_id')
    
    # Get all events for this coordinator
    if coordinator_id:
        events = Event.objects.filter(coordinator_id=coordinator_id).order_by('-created_at')
    else:
        events = Event.objects.all().order_by('-created_at')
    
    return render(request, "coordinator/coordinator_shifts_list.html", {"events": events})

# Coordinator manage shifts page
def coordinator_manage_shifts_page(request, event_id):
    return render(request, "coordinator/coordinator_manage_shifts.html", {"event_id": event_id})

# Coordinator request list page
def coordinator_request_list_page(request):
    return render(request, "coordinator/coordinator_request_list.html")

# Coordinator request detail page
def coordinator_request_detail_page(request, request_id):
    return render(request, "coordinator/coordinator_request_detail.html", {"request_id": request_id})

# Coordinator volunteer profile page
def coordinator_volunteer_profile_page(request, volunteer_id):
    return render(request, "coordinator/coordinator_volunteer_profile.html", {"volunteer_id": volunteer_id})

# Coordinator volunteer summary page
def coordinator_volunteer_summary_page(request, volunteer_id):
    return render(request, "coordinator/coordinator_volunteer_summary.html", {"volunteer_id": volunteer_id})

# Coordinator certificate review page
def coordinator_certificate_review_page(request):
    return render(request, "coordinator/coordinator_certificate_review.html")


# -----------------------------------------------------
# API VIEWSETS
# -----------------------------------------------------

class CoordinatorViewSet(viewsets.ModelViewSet):
    queryset = Coordinator.objects.all()
    serializer_class = CoordinatorSerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current logged-in coordinator based on session.
        """
        coordinator_email = request.session.get('coordinator_email')
        if not coordinator_email:
            return Response({'error': 'Not logged in'}, status=401)
        
        try:
            coordinator = Coordinator.objects.get(email=coordinator_email)
            serializer = self.get_serializer(coordinator)
            return Response(serializer.data)
        except Coordinator.DoesNotExist:
            return Response({'error': 'Coordinator not found'}, status=404)

    def create(self, request, *args, **kwargs):
        # Extract password from request data
        password = request.data.get('password')
        email = request.data.get('email')
        name = request.data.get('name', '')
        
        # Check if coordinator with this email already exists
        if Coordinator.objects.filter(email=email).exists():
            return Response({'error': 'A coordinator with this email already exists.'}, status=400)
        
        # Create User account first
        from django.contrib.auth.models import User
        try:
            username = email.split('@')[0]  # Use email prefix as username
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                # Try to use the existing user if emails match
                existing_user = User.objects.get(username=username)
                if existing_user.email != email:
                    # Username conflict with different email - add a random suffix
                    import random
                    username = f"{username}{random.randint(100, 999)}"
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.first_name = name
                    user.save()
                # If emails match, the user already signed up - continue to create coordinator
            else:
                # Create new user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.first_name = name
                user.save()
        except Exception as e:
            return Response({'error': f'Failed to create user account: {str(e)}'}, status=400)
        
        # Now create coordinator without password field
        try:
            coordinator = Coordinator.objects.create(
                name=request.data.get('name'),
                email=request.data.get('email'),
                phone=request.data.get('phone', ''),
                address=request.data.get('address', ''),
                organization=request.data.get('organization', ''),
                active=True
            )
            serializer = self.get_serializer(coordinator)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({'error': f'Failed to create coordinator: {str(e)}'}, status=400)


class VolunteerViewSet(viewsets.ModelViewSet):
    queryset = Volunteer.objects.all()
    serializer_class = VolunteerSerializer

    def create(self, request, *args, **kwargs):
        # Extract password from request data
        password = request.data.get('password')
        email = request.data.get('email')
        name = request.data.get('name', '')
        
        # Create User account
        from django.contrib.auth.models import User
        username = email.split('@')[0]  # Use email prefix as username
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = name
        user.save()
        
        # Continue with normal volunteer creation
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        volunteer = self.get_object()

        enrollments = Enrollment.objects.filter(volunteer=volunteer)
        certificates = Certificate.objects.filter(user=volunteer)

        data = {
            "volunteer": VolunteerSerializer(volunteer).data,
            "enrollments": EnrollmentSerializer(enrollments, many=True).data,
            "certificates": CertificateSerializer(certificates, many=True).data,
        }
        return Response(data)

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get the currently logged-in volunteer"""
        if not request.user.is_authenticated:
            return Response(
                {"error": "User is not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            volunteer = Volunteer.objects.get(email=request.user.email)
            serializer = self.get_serializer(volunteer)
            return Response(serializer.data)
        except Volunteer.DoesNotExist:
            # Try to find by username
            try:
                volunteer = Volunteer.objects.get(email=request.user.username)
                serializer = self.get_serializer(volunteer)
                return Response(serializer.data)
            except Volunteer.DoesNotExist:
                return Response(
                    {"error": "Volunteer record not found for this user"},
                    status=status.HTTP_404_NOT_FOUND
                )


class CertificateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateSerializer

    def get_queryset(self):
        """Only return certificates that have files (actual uploads)"""
        queryset = Certificate.objects.filter(file__isnull=False).exclude(file="")
        
        # Filter by event if provided
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        return queryset


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer

    def get_queryset(self):
        queryset = Role.objects.all()
        language_level = self.request.query_params.get('language_level')
        task_complexity = self.request.query_params.get('task_complexity')
        if language_level:
            queryset = queryset.filter(language_level=language_level)
        if task_complexity:
            queryset = queryset.filter(task_complexity=task_complexity)
        return queryset


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def create(self, request, *args, **kwargs):
        volunteer_id = request.data.get('volunteer')
        role_id = request.data.get('role')
        if volunteer_id and role_id:
            enrollment = Enrollment.objects.create(
                volunteer_id=volunteer_id,
                role_id=role_id,
                hours_worked=request.data.get('hours_worked', 0)
            )
            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data)
        return Response({'error': 'volunteer and role IDs required'}, status=400)


class CulturalInterestViewSet(viewsets.ModelViewSet):
    queryset = CulturalInterest.objects.all()
    serializer_class = CulturalInterestSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]


class VolunteerWorkPhotoViewSet(viewsets.ModelViewSet):
    queryset = VolunteerWorkPhoto.objects.all()
    serializer_class = VolunteerWorkPhotoSerializer
    parser_classes = [MultiPartParser, FormParser]
