from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Candidate CRUD operations
    path('', views.candidate_list, name='candidate_list'),
    path('create/', views.candidate_create, name='candidate_create'),
    path('<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('<int:pk>/edit/', views.candidate_update, name='candidate_update'),
    path('<int:pk>/delete/', views.candidate_delete, name='candidate_delete'),

    # Qualification management
    path('<int:candidate_pk>/qualifications/add/', views.qualification_create, name='qualification_create'),

    # Experience management
    path('<int:candidate_pk>/experiences/add/', views.experience_create, name='experience_create'),

    # Bulk actions and exports
    path('bulk-actions/', views.bulk_actions, name='bulk_actions'),

    # API endpoints
    path('api/search/', views.candidate_search_api, name='candidate_search_api'),

    # Plan management
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:pk>/edit/', views.plan_update, name='plan_update'),
    path('plans/<int:pk>/delete/', views.plan_delete, name='plan_delete'),


    # Plan-based evaluation
    path('evaluation/', views.plan_selection_for_evaluation, name='plan_selection_for_evaluation'),
    path('evaluation/<int:pk>/', views.plan_evaluation, name='plan_evaluation'),
]