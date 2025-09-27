from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Decorator that requires user to be an admin"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:home')
    return wrapper

def committee_required(view_func):
    """Decorator that requires user to be a committee member or admin"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and (request.user.profile.is_committee_member or request.user.profile.is_admin):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:home')
    return wrapper

def evaluator_required(view_func):
    """Decorator that requires user to be an active evaluator"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.can_evaluate_candidates:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to evaluate candidates.')
            return redirect('core:home')
    return wrapper

def candidate_manager_required(view_func):
    """Decorator that requires user to be able to manage candidates"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.can_manage_candidates:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to manage candidates.')
            return redirect('core:home')
    return wrapper

def examiner_required(view_func):
    """Decorator that requires user to be an examiner or admin"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and (request.user.profile.is_examiner or request.user.profile.is_admin):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access examiner functions.')
            return redirect('core:home')
    return wrapper

def session_controller_required(view_func):
    """Decorator that requires user to be able to control evaluation sessions"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.can_control_sessions:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to control evaluation sessions.')
            return redirect('core:home')
    return wrapper

def report_access_required(view_func):
    """Decorator that requires user to be able to generate reports"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.can_generate_reports:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access reports.')
            return redirect('core:home')
    return wrapper

def examinee_required(view_func):
    """Decorator that requires user to be an examinee"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'profile') and request.user.profile.is_examinee:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page. Only examinees can access this area.')
            return redirect('core:home')
    return wrapper