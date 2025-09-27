from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from students.models import Person as Candidate, Plan
from .models import UserProfile
from .decorators import admin_required, committee_required


def signing(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user type
            if hasattr(user, 'profile'):
                if user.profile.is_admin:
                    return redirect('accounts:admin_dashboard')
                elif user.profile.is_committee_member:
                    return redirect('accounts:committee_dashboard')
                elif user.profile.is_examinee:
                    return redirect('evaluation:examinee_dashboard')
            return redirect('core:home')
        else:
            messages.error(request, 'Username or password is incorrect.')

    return render(request, 'accounts/signing.html')


def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect("accounts:signing")


@login_required
def dashboard(request):
    """General dashboard that redirects to appropriate dashboard based on user type"""
    if hasattr(request.user, 'profile'):
        if request.user.profile.is_admin:
            return redirect('accounts:admin_dashboard')
        elif request.user.profile.is_committee_member or request.user.profile.user_type == 'committee':
            return redirect('accounts:committee_dashboard')
        elif request.user.profile.user_type == 'examiner':
            return redirect('evaluation:examiner_dashboard')
        elif request.user.profile.is_examinee:
            return redirect('evaluation:examinee_dashboard')
    return redirect('core:home')


@admin_required
def admin_dashboard(request):
    """Dashboard for admin users with full access"""
    context = {
        'total_candidates': Candidate.objects.count(),
        'total_users': User.objects.count(),
        'total_plans': Plan.objects.count(),
        'active_plans': Plan.objects.filter(is_active=True).count(),
        'inactive_plans': Plan.objects.filter(is_active=False).count(),
        'total_admins': UserProfile.objects.filter(user_type='admin').count(),
        'total_committee_members': UserProfile.objects.filter(user_type='committee').count(),
        'active_evaluators': UserProfile.objects.filter(is_active_evaluator=True).count(),
        'recent_candidates': Candidate.objects.order_by('-created_at')[:5],
        'recent_plans': Plan.objects.order_by('-created_at')[:5],
        'user_type': 'admin',
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@committee_required
def committee_dashboard(request):
    """Committee member dashboard showing current evaluation status"""
    from evaluation.models import EvaluationSession, CandidateEvaluation
    from django.utils import timezone

    # Find active sessions where user can evaluate
    active_sessions = EvaluationSession.objects.filter(
        status='active'
    ).select_related('plan', 'current_candidate', 'examiner')

    # No need to calculate progress - the model already has these as properties

    # Get user's pending evaluations
    pending_evaluations = CandidateEvaluation.objects.filter(
        evaluator=request.user,
        is_completed=False
    ).select_related('candidate', 'session')

    # Get user's completed evaluations today
    today_evaluations = CandidateEvaluation.objects.filter(
        evaluator=request.user,
        start_time__date=timezone.now().date()
    ).select_related('candidate', 'session')

    context = {
        'title': 'لوحة تحكم لجنة التقييم',
        'active_sessions': active_sessions,
        'pending_evaluations': pending_evaluations,
        'today_evaluations': today_evaluations,
        'total_evaluations': CandidateEvaluation.objects.filter(evaluator=request.user).count(),
        'completed_today': today_evaluations.filter(is_completed=True).count(),
    }
    return render(request, 'evaluation/committee/dashboard.html', context)


@admin_required
def user_management(request):
    """User management page for admins"""
    users = User.objects.select_related('profile').all()
    context = {
        'users': users,
        'total_users': users.count(),
        'user_type': 'admin',
    }
    return render(request, 'accounts/user_management.html', context)
