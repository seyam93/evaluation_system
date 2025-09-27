from django.shortcuts import render
from students.models import Plan
from evaluation.models import EvaluationSession
from django.db.models import Count


def home(request):
    context = {}

    if request.user.is_authenticated:
        user_type = request.user.profile.user_type

        if user_type == 'examiner':
            # Examiner Dashboard Data
            context.update({
                'user_type': 'examiner',
                'total_sessions': EvaluationSession.objects.filter(examiner=request.user).count(),
                'active_sessions': EvaluationSession.objects.filter(
                    examiner=request.user,
                    status='active'
                ),
                'recent_sessions': EvaluationSession.objects.filter(
                    examiner=request.user
                ).order_by('-session_date')[:5],
                'available_plans': Plan.objects.filter(
                    is_active=True,
                    candidates__isnull=False
                ).distinct().count(),
            })

        elif user_type == 'committee':
            # Redirect committee members (evaluators) to their specialized dashboard
            from django.shortcuts import redirect
            return redirect('accounts:committee_dashboard')

        elif user_type == 'examinee':
            # Redirect examinees to their dashboard
            from django.shortcuts import redirect
            return redirect('evaluation:examinee_dashboard')

        elif user_type == 'admin':
            # Admin Dashboard Data
            context.update({
                'user_type': 'admin',
                'total_plans': Plan.objects.count(),
                'active_plans': Plan.objects.filter(is_active=True),
                'total_sessions': EvaluationSession.objects.count(),
                'active_sessions': EvaluationSession.objects.filter(status='active'),
                'recent_activity': EvaluationSession.objects.order_by('-created_at')[:5],
            })
        else:
            # Default user - show basic plan info
            context.update({
                'user_type': 'default',
                'active_plans': Plan.objects.filter(is_active=True).order_by('-created_at')[:6],
            })
    else:
        # Anonymous user - show basic info
        context.update({
            'user_type': 'anonymous',
            'active_plans': Plan.objects.filter(is_active=True).order_by('-created_at')[:3],
        })

    return render(request, 'core/home.html', context)
