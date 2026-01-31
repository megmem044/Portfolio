# File: signups/admin.py
# Purpose:
#   Register models with Django admin interface for easy management

from django.contrib import admin
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

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'active']
    list_filter = ['active']
    search_fields = ['name', 'email']

@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'organization', 'active', 'created_at']
    list_filter = ['active', 'organization', 'created_at']
    search_fields = ['name', 'email', 'organization']

@admin.register(Role)  
class RoleAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'coordinator', 'language_level', 'task_complexity']
    list_filter = ['language_level', 'task_complexity', 'date', 'coordinator']
    search_fields = ['title', 'location']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'role', 'status', 'hours_worked', 'enrolled_date']
    list_filter = ['status', 'enrolled_date']
    search_fields = ['volunteer__name', 'role__title']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'uploaded_at']
    list_filter = ['status', 'uploaded_at']

@admin.register(CulturalInterest)
class CulturalInterestAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'content', 'author']

@admin.register(VolunteerWorkPhoto)
class VolunteerWorkPhotoAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['caption', 'enrollment__volunteer__name']
