from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

class UserProfileMixin:
    """Base mixin to check if user has a profile"""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(LoginRequiredMixin, UserProfileMixin):
    """Mixin that requires user to be an admin"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code == 302:
            return response

        if not request.user.profile.is_admin:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')

        return response

class CommitteeRequiredMixin(LoginRequiredMixin, UserProfileMixin):
    """Mixin that requires user to be a committee member or admin"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code == 302:
            return response

        if not (request.user.profile.is_committee_member or request.user.profile.is_admin):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')

        return response

class EvaluatorRequiredMixin(LoginRequiredMixin, UserProfileMixin):
    """Mixin that requires user to be an active evaluator"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code == 302:
            return response

        if not request.user.profile.can_evaluate_candidates:
            messages.error(request, 'You do not have permission to evaluate candidates.')
            return redirect('home')

        return response

class CandidateManagerRequiredMixin(LoginRequiredMixin, UserProfileMixin):
    """Mixin that requires user to be able to manage candidates"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code == 302:
            return response

        if not request.user.profile.can_manage_candidates:
            messages.error(request, 'You do not have permission to manage candidates.')
            return redirect('home')

        return response

class ReportAccessRequiredMixin(LoginRequiredMixin, UserProfileMixin):
    """Mixin that requires user to be able to generate reports"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, 'status_code') and response.status_code == 302:
            return response

        if not request.user.profile.can_generate_reports:
            messages.error(request, 'You do not have permission to access reports.')
            return redirect('home')

        return response