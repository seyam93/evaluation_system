from django.urls import path
from . import views

app_name = 'examinations'

urlpatterns = [
    path('test-templates/', views.test_templates_list, name='test_templates_list'),
    path('test-template/create/', views.test_template_create, name='test_template_create'),
    path('test-template/<int:pk>/update/', views.test_template_update, name='test_template_update'),
    path('test-template/<int:pk>/delete/', views.test_template_delete, name='test_template_delete'),
    path('test-template/<int:pk>/toggle-active/', views.test_template_toggle_active, name='test_template_toggle_active'),
]