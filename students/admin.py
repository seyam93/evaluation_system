from django.contrib import admin
from .models import Person, Qualification, Experience, Plan

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'plan', 'application_status', 'birth_date', 'gender', 'university', 'general_degree', 'created_at']
    list_filter = ['gender', 'general_degree', 'marital_status', 'graduation_year', 'plan', 'application_status']
    search_fields = ['student_name', 'email', 'phone_number', 'plan__title']
    readonly_fields = ['created_at', 'updated_at', 'age', 'application_date']

    fieldsets = (
        ('Personal Information', {
            'fields': ('student_name', 'personal_image', 'birth_date', 'gender', 'marital_status', 'number_of_children')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address')
        }),
        ('Education', {
            'fields': ('primary_qualification', 'university', 'general_degree', 'graduation_year')
        }),
        ('Application Information', {
            'fields': ('plan', 'application_status', 'application_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ['degree_name', 'person', 'degree_date']
    list_filter = ['degree_date']
    search_fields = ['degree_name', 'person__student_name']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company_name', 'person', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['job_title', 'company_name', 'person__student_name']

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'is_active', 'candidates_count', 'created_at', 'updated_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['title', 'department']
    readonly_fields = ['created_at', 'updated_at', 'candidates_count']

    fieldsets = (
        ('Plan Information', {
            'fields': ('title', 'department', 'is_active', 'notes')
        }),
        ('Statistics', {
            'fields': ('candidates_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def candidates_count(self, obj):
        return obj.candidates_count
    candidates_count.short_description = 'Number of Candidates'

