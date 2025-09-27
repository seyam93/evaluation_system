from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.signing, name='signing'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('committee-dashboard/', views.committee_dashboard, name='committee_dashboard'),
    path('user-management/', views.user_management, name='user_management'),
]