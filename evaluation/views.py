from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import examiner_required, evaluator_required, examinee_required
from students.models import Plan
from .models import (
    EvaluationSession, EvaluationQuestion, CandidateEvaluation,
    EvaluationAnswer, EvaluationTemplate
)
from .forms import EvaluationSessionForm, CandidateEvaluationForm, EvaluationQuestionForm


# Examiner Views
@examiner_required
def examiner_dashboard(request):
    """Examiner dashboard showing session overview"""
    user_sessions = EvaluationSession.objects.filter(
        examiner=request.user
    ).order_by('-session_date')[:5]

    active_sessions = EvaluationSession.objects.filter(
        examiner=request.user,
        status='active'
    )

    context = {
        'title': 'لوحة تحكم المشرف',
        'recent_sessions': user_sessions,
        'active_sessions': active_sessions,
        'total_sessions': EvaluationSession.objects.filter(examiner=request.user).count(),
        'completed_sessions': EvaluationSession.objects.filter(
            examiner=request.user, status='completed'
        ).count(),
    }

    return render(request, 'evaluation/examiner/dashboard.html', context)


@examiner_required
def session_list(request):
    """List all evaluation sessions for the examiner"""
    sessions = EvaluationSession.objects.filter(
        examiner=request.user
    ).select_related('plan', 'current_candidate').order_by('-session_date')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        sessions = sessions.filter(
            Q(plan__title__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        sessions = sessions.filter(status=status_filter)

    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'جلسات التقييم',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': EvaluationSession.SESSION_STATUS,
    }

    return render(request, 'evaluation/examiner/session_list.html', context)


@examiner_required
def plan_selection(request):
    """Plan selection page for creating evaluation sessions"""
    from django.core.paginator import Paginator

    # Get all active plans with candidates
    plans = Plan.objects.filter(
        candidates__isnull=False
    ).distinct().select_related().prefetch_related(
        'candidates', 'evaluation_sessions'
    ).order_by('-created_at')

    # Apply search filter
    search_query = request.GET.get('search')
    if search_query:
        plans = plans.filter(
            Q(title__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    # Apply status filter
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        plans = plans.filter(is_active=True)
    elif status_filter == 'inactive':
        plans = plans.filter(is_active=False)

    # Add evaluation progress data to each plan
    for plan in plans:
        total_candidates = plan.candidates.count()
        # Count unique candidates who have completed evaluations
        from evaluation.models import CandidateEvaluation
        evaluated_candidates = CandidateEvaluation.objects.filter(
            session__plan=plan,
            is_completed=True
        ).values('candidate').distinct().count()

        plan.total_candidates = total_candidates
        plan.evaluated_candidates = evaluated_candidates
        plan.progress_percentage = round((evaluated_candidates / total_candidates * 100), 1) if total_candidates > 0 else 0

    # Pagination
    paginator = Paginator(plans, 6)  # 6 plans per page
    page = request.GET.get('page')
    plans = paginator.get_page(page)

    context = {
        'title': 'اختيار خطة التوظيف',
        'plans': plans,
    }

    return render(request, 'evaluation/examiner/plan_selection.html', context)


@examiner_required
def session_create(request):
    """Create a new evaluation session"""
    if request.method == 'POST':
        form = EvaluationSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.examiner = request.user
            session.save()
            messages.success(request, f'تم إنشاء جلسة التقييم لخطة "{session.plan.title}" بنجاح.')
            return redirect('evaluation:session_detail', session_id=session.id)
    else:
        form = EvaluationSessionForm()

    context = {
        'title': 'إنشاء جلسة تقييم جديدة',
        'form': form,
    }

    return render(request, 'evaluation/examiner/session_form.html', context)


@examiner_required
def session_create_for_plan(request, plan_id):
    """Create a new evaluation session for a specific plan"""
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)

    if request.method == 'POST':
        form = EvaluationSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.examiner = request.user
            session.plan = plan  # Set the plan automatically
            session.save()
            messages.success(request, f'تم إنشاء جلسة التقييم لخطة "{session.plan.title}" بنجاح.')
            return redirect('evaluation:session_detail', session_id=session.id)
    else:
        # Pre-populate the form with the selected plan
        form = EvaluationSessionForm(initial={'plan': plan})
        # Make the plan field readonly
        form.fields['plan'].widget.attrs['readonly'] = True
        form.fields['plan'].widget.attrs['style'] = 'background-color: #e9ecef;'

    context = {
        'title': f'إنشاء جلسة تقييم - {plan.title}',
        'form': form,
        'plan': plan,
        'selected_plan': True,
    }

    return render(request, 'evaluation/examiner/session_form.html', context)


@examiner_required
def session_detail(request, session_id):
    """Detailed view of an evaluation session"""
    session = get_object_or_404(
        EvaluationSession,
        id=session_id,
        examiner=request.user
    )

    evaluations = session.candidate_evaluations.select_related(
        'candidate', 'evaluator'
    ).order_by('-start_time')

    # Get all candidates from this session's plan
    all_candidates = session.plan.candidates.all().order_by('student_name')

    context = {
        'title': f'جلسة تقييم - {session.plan.title}',
        'session': session,
        'evaluations': evaluations,
        'all_candidates': all_candidates,
        'can_start': session.status == 'setup',
        'can_pause': session.status == 'active',
        'can_resume': session.status == 'paused',
        'can_complete': session.status in ['active', 'paused'],
    }

    return render(request, 'evaluation/examiner/session_detail.html', context)


@examiner_required
def set_current_candidate(request, session_id):
    """Set the current candidate for an evaluation session"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        import json
        from django.http import JsonResponse

        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            candidate_id = data.get('candidate_id')
        else:
            candidate_id = request.POST.get('candidate_id')

        if not candidate_id:
            return JsonResponse({'error': 'لم يتم تحديد المرشح'}, status=400)

        # Optimized query - single database hit
        session = EvaluationSession.objects.select_related('plan').get(
            id=session_id,
            examiner=request.user
        )

        # Verify candidate belongs to plan and update in one go
        candidate = session.plan.candidates.get(id=candidate_id)

        # Ultra-fast update - only update the specific field
        EvaluationSession.objects.filter(id=session_id).update(
            current_candidate_id=candidate_id
        )

        return JsonResponse({
            'success': True,
            'candidate_name': candidate.student_name,
            'message': f'تم اختيار {candidate.student_name} كمرشح حالي'
        })

    except EvaluationSession.DoesNotExist:
        return JsonResponse({'error': 'الجلسة غير موجودة'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'حدث خطأ أثناء تحديث المرشح'}, status=500)


@examiner_required
def session_start(request, session_id):
    """Start an evaluation session"""
    session = get_object_or_404(
        EvaluationSession,
        id=session_id,
        examiner=request.user
    )

    if request.method == 'POST' and session.status == 'setup':
        session.start_session()
        messages.success(request, 'تم بدء جلسة التقييم بنجاح.')
        return JsonResponse({'success': True, 'status': session.status})

    return JsonResponse({'success': False, 'error': 'Cannot start session'})


@examiner_required
def session_pause(request, session_id):
    """Pause an active evaluation session"""
    session = get_object_or_404(
        EvaluationSession,
        id=session_id,
        examiner=request.user
    )

    if request.method == 'POST' and session.status == 'active':
        session.pause_session()
        messages.success(request, 'تم إيقاف جلسة التقييم مؤقتاً.')
        return JsonResponse({'success': True, 'status': session.status})

    return JsonResponse({'success': False, 'error': 'Cannot pause session'})


@examiner_required
def session_resume(request, session_id):
    """Resume a paused evaluation session"""
    session = get_object_or_404(
        EvaluationSession,
        id=session_id,
        examiner=request.user
    )

    if request.method == 'POST' and session.status == 'paused':
        session.resume_session()
        messages.success(request, 'تم استئناف جلسة التقييم.')
        return JsonResponse({'success': True, 'status': session.status})

    return JsonResponse({'success': False, 'error': 'Cannot resume session'})


@examiner_required
def session_complete(request, session_id):
    """Complete an evaluation session"""
    session = get_object_or_404(
        EvaluationSession,
        id=session_id,
        examiner=request.user
    )

    if request.method == 'POST' and session.status in ['active', 'paused']:
        session.complete_session()
        messages.success(request, 'تم إنهاء جلسة التقييم بنجاح.')
        return JsonResponse({'success': True, 'status': session.status})

    return JsonResponse({'success': False, 'error': 'Cannot complete session'})


@examiner_required
def next_candidate(request, session_id):
    """Move to the next candidate in the evaluation queue"""
    session = get_object_or_404(
        EvaluationSession,
        id=session_id,
        examiner=request.user
    )

    if request.method == 'POST' and session.status == 'active':
        next_candidate = session.get_next_candidate()
        if next_candidate:
            session.current_candidate = next_candidate
            session.save()

            # Create a new evaluation record for the candidate
            CandidateEvaluation.objects.create(
                session=session,
                candidate=next_candidate,
                evaluator=request.user
            )

            messages.success(request, f'تم الانتقال إلى المرشح التالي: {next_candidate.student_name}')
            return JsonResponse({
                'success': True,
                'candidate_name': next_candidate.student_name,
                'candidate_id': next_candidate.id
            })
        else:
            messages.info(request, 'لا يوجد مرشحين متبقيين للتقييم.')
            return JsonResponse({'success': False, 'error': 'No more candidates'})

    return JsonResponse({'success': False, 'error': 'Cannot move to next candidate'})


# Committee Member Views
@evaluator_required
def committee_dashboard(request):
    """Committee member dashboard showing current evaluation status"""
    # Find active sessions where user can evaluate
    active_sessions = EvaluationSession.objects.filter(
        status='active'
    ).select_related('plan', 'current_candidate', 'examiner').prefetch_related(
        'current_candidate__qualifications',
        'current_candidate__experiences',
        'current_candidate__test_results__test_category'
    )

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


@evaluator_required
def current_candidate_view(request):
    """Show the current candidate being evaluated"""
    # Find active sessions with current candidates
    active_sessions = EvaluationSession.objects.filter(
        status='active'
    ).exclude(current_candidate__isnull=True).select_related(
        'current_candidate', 'plan', 'examiner'
    )

    if not active_sessions.exists():
        context = {
            'title': 'التقييم الحالي',
            'no_active_session': True,
            'message': 'لا توجد جلسات تقييم نشطة حالياً.'
        }
        return render(request, 'evaluation/committee/current_candidate.html', context)

    # For now, show the first active session (in real app, might need to filter by user access)
    session = active_sessions.first()
    current_candidate = session.current_candidate

    # Check if user already has an evaluation for this candidate in this session
    existing_evaluation = CandidateEvaluation.objects.filter(
        session=session,
        candidate=current_candidate,
        evaluator=request.user
    ).first()

    context = {
        'title': 'التقييم الحالي',
        'session': session,
        'candidate': current_candidate,
        'existing_evaluation': existing_evaluation,
        'can_evaluate': not existing_evaluation or not existing_evaluation.is_completed,
    }

    return render(request, 'evaluation/committee/current_candidate.html', context)


@evaluator_required
def committee_exam(request):
    """Committee exam interface - shows both questions and answers"""
    # Get the active session
    active_session = EvaluationSession.objects.filter(
        status='active'
    ).select_related('plan', 'current_candidate').first()

    if not active_session:
        messages.error(request, 'لا توجد جلسة تقييم نشطة.')
        return redirect('accounts:committee_dashboard')

    # Get all available questions
    questions = EvaluationQuestion.objects.filter(is_active=True)

    context = {
        'title': 'واجهة الأسئلة للجنة',
        'active_session': active_session,
        'questions': questions,
    }

    return render(request, 'evaluation/committee/exam.html', context)


@evaluator_required
def candidate_evaluate(request, evaluation_id):
    """Evaluate a specific candidate"""
    evaluation = get_object_or_404(
        CandidateEvaluation,
        id=evaluation_id,
        evaluator=request.user
    )

    # Get evaluation questions
    questions = EvaluationQuestion.objects.filter(is_active=True).order_by('created_at')

    if request.method == 'POST':
        form = CandidateEvaluationForm(request.POST, instance=evaluation)

        # Process individual question scores and notes
        total_score = 0
        question_count = 0

        for question in questions:
            score_key = f'question_{question.id}_score'
            notes_key = f'question_{question.id}_notes'

            score = request.POST.get(score_key, 0)
            notes = request.POST.get(notes_key, '')

            try:
                score = float(score)
                total_score += score
                question_count += 1
            except (ValueError, TypeError):
                score = 0

            # Create or update the answer
            answer, created = EvaluationAnswer.objects.get_or_create(
                evaluation=evaluation,
                question=question,
                defaults={
                    'score': score,
                    'notes': notes,
                    'text_answer': f'إجابة شفهية - درجة: {score}/10'
                }
            )

            if not created:
                answer.score = score
                answer.notes = notes
                answer.text_answer = f'إجابة شفهية - درجة: {score}/10'
                answer.save()

        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.total_score = total_score
            evaluation.max_possible_score = question_count * 10  # Each question out of 10
            evaluation.save()

            evaluation.complete_evaluation()
            messages.success(request, f'تم حفظ تقييم المرشح "{evaluation.candidate.student_name}" بنجاح.')
            return redirect('evaluation:committee_current_candidate')
    else:
        form = CandidateEvaluationForm(instance=evaluation)

    # Get existing answers
    existing_answers = {
        answer.question.id: answer
        for answer in evaluation.answers.select_related('question')
    }

    context = {
        'title': f'تقييم المرشح - {evaluation.candidate.student_name}',
        'form': form,
        'evaluation': evaluation,
        'questions': questions,
        'existing_answers': existing_answers,
    }

    return render(request, 'evaluation/committee/evaluate_candidate.html', context)


@evaluator_required
def create_evaluation(request):
    """Create a new evaluation for current candidate"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        session_id = data.get('session_id')
        candidate_id = data.get('candidate_id')

        try:
            session = EvaluationSession.objects.get(id=session_id, status='active')
            candidate = session.current_candidate

            if candidate and candidate.id == candidate_id:
                # Create evaluation
                evaluation, created = CandidateEvaluation.objects.get_or_create(
                    session=session,
                    candidate=candidate,
                    evaluator=request.user,
                    defaults={
                        'total_score': 0.0,
                        'max_possible_score': 0.0,
                    }
                )

                return JsonResponse({
                    'success': True,
                    'evaluation_url': f'/evaluation/committee/evaluate/{evaluation.id}/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'المرشح غير متاح للتقييم'
                })

        except EvaluationSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'الجلسة غير موجودة أو غير نشطة'
            })

    return JsonResponse({'success': False, 'error': 'طريقة طلب غير صحيحة'})


# AJAX Views
@login_required
def ajax_session_status(request, session_id):
    """Get current session status via AJAX"""
    try:
        session = EvaluationSession.objects.select_related(
            'current_candidate', 'plan'
        ).get(id=session_id)

        data = {
            'status': session.status,
            'current_candidate': {
                'id': session.current_candidate.id if session.current_candidate else None,
                'name': session.current_candidate.student_name if session.current_candidate else None,
            },
            'progress': session.progress_percentage,
            'evaluated_count': session.evaluated_candidates_count,
            'total_count': session.total_candidates,
        }

        return JsonResponse({'success': True, 'data': data})
    except EvaluationSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'})


@evaluator_required
def ajax_current_candidate(request):
    """Get current candidate being evaluated via AJAX"""
    active_sessions = EvaluationSession.objects.filter(
        status='active'
    ).exclude(current_candidate__isnull=True).select_related(
        'current_candidate', 'plan'
    )

    if active_sessions.exists():
        session = active_sessions.first()
        data = {
            'session_id': session.id,
            'plan_title': session.plan.title,
            'candidate': {
                'id': session.current_candidate.id,
                'name': session.current_candidate.student_name,
                'national_id': session.current_candidate.national_id,
            },
            'has_active_candidate': True,
        }
    else:
        data = {
            'has_active_candidate': False,
            'message': 'لا يوجد مرشح قيد التقييم حالياً.'
        }

    return JsonResponse({'success': True, 'data': data})


# Question Management Views
@examiner_required
def question_list(request):
    """List all evaluation questions"""
    questions = EvaluationQuestion.objects.all().order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        questions = questions.filter(
            Q(question_text__icontains=search_query) |
            Q(answer__icontains=search_query)
        )

    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        questions = questions.filter(question_type=type_filter)

    paginator = Paginator(questions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'إدارة أسئلة التقييم',
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'question_types': EvaluationQuestion.QUESTION_TYPES,
    }

    return render(request, 'evaluation/questions/question_list.html', context)


@examiner_required
def question_create(request):
    """Create a new evaluation question"""
    if request.method == 'POST':
        form = EvaluationQuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            messages.success(request, f'تم إنشاء السؤال بنجاح.')
            return redirect('evaluation:question_list')
    else:
        form = EvaluationQuestionForm()

    context = {
        'title': 'إضافة سؤال تقييم جديد',
        'form': form,
        'is_edit': False,
    }

    return render(request, 'evaluation/questions/question_form.html', context)


@examiner_required
def question_update(request, question_id):
    """Update an existing evaluation question"""
    question = get_object_or_404(EvaluationQuestion, id=question_id)

    if request.method == 'POST':
        form = EvaluationQuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            messages.success(request, f'تم تحديث السؤال بنجاح.')
            return redirect('evaluation:question_list')
    else:
        form = EvaluationQuestionForm(instance=question)

    context = {
        'title': f'تعديل السؤال - {question.question_text[:50]}...',
        'form': form,
        'question': question,
        'is_edit': True,
    }

    return render(request, 'evaluation/questions/question_form.html', context)


@examiner_required
def question_delete(request, question_id):
    """Delete an evaluation question"""
    if request.method == 'POST':
        question = get_object_or_404(EvaluationQuestion, id=question_id)
        question_preview = question.question_text[:50] + '...'
        question.delete()
        messages.success(request, f'تم حذف السؤال "{question_preview}" بنجاح.')

    return redirect('evaluation:question_list')


@examiner_required
def question_detail(request, question_id):
    """View question details including sample answer"""
    question = get_object_or_404(EvaluationQuestion, id=question_id)

    context = {
        'title': f'تفاصيل السؤال - {question.question_text[:50]}...',
        'question': question,
    }

    return render(request, 'evaluation/questions/question_detail.html', context)


@login_required
def get_random_qa_question(request):
    """Get a random question for the examinee (any type)"""
    import random

    # Get all active questions
    questions = list(EvaluationQuestion.objects.filter(is_active=True))

    if questions:
        random_question = random.choice(questions)

        # Update the current question in the active session
        try:
            active_session = EvaluationSession.objects.filter(status='active').first()
            if active_session:
                active_session.current_question = random_question
                active_session.save(update_fields=['current_question'])
        except Exception as e:
            pass  # Don't fail if session update fails

        data = {
            'success': True,
            'question': random_question.question_text,
            'question_type': random_question.question_type,
            'id': random_question.id,
        }

        # Add options for MCQ questions
        if random_question.question_type == 'mcq':
            options = []
            if random_question.option_a: options.append(random_question.option_a)
            if random_question.option_b: options.append(random_question.option_b)
            if random_question.option_c: options.append(random_question.option_c)
            if random_question.option_d: options.append(random_question.option_d)
            data['options'] = options

        # Don't include answers for examinee
    else:
        data = {
            'success': False,
            'message': 'لا توجد أسئلة متاحة.'
        }

    return JsonResponse(data)


@evaluator_required
def get_qa_question_with_answer(request, question_id):
    """Get Q&A question with sample answer for committee members"""
    question = get_object_or_404(
        EvaluationQuestion,
        id=question_id,
        question_type='qa',
        is_active=True
    )

    data = {
        'success': True,
        'question': {
            'id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'answer': question.answer,
            'correct_answer': question.correct_answer,
        }
    }

    return JsonResponse(data)


# Examinee Views
@examinee_required
def examinee_dashboard(request):
    """Simple examinee dashboard showing current candidate and start exam button"""
    # Get the most recent active session with current candidate
    active_session = EvaluationSession.objects.filter(
        status='active'
    ).select_related('plan', 'current_candidate').first()

    context = {
        'title': 'لوحة المرشح',
        'active_session': active_session,
        'user_info': {
            'name': request.user.get_full_name() or request.user.username,
            'user_type': request.user.profile.get_user_type_display() if hasattr(request.user, 'profile') else 'Unknown',
        }
    }

    return render(request, 'evaluation/examinee/dashboard.html', context)


@examinee_required
def examinee_exam(request):
    """Exam interface for examinee - shows questions only without answers"""
    # Get the active session
    active_session = EvaluationSession.objects.filter(
        status='active'
    ).select_related('plan', 'current_candidate').first()

    if not active_session or not active_session.current_candidate:
        messages.error(request, 'لا توجد جلسة تقييم نشطة أو لا يوجد مرشح حالي.')
        return redirect('evaluation:examinee_dashboard')

    # Get all available questions
    questions = EvaluationQuestion.objects.filter(is_active=True)

    context = {
        'title': 'واجهة الاختبار',
        'active_session': active_session,
        'questions': questions,
        'user_info': {
            'name': request.user.get_full_name() or request.user.username,
            'user_type': request.user.profile.get_user_type_display() if hasattr(request.user, 'profile') else 'Unknown',
        }
    }

    return render(request, 'evaluation/examinee/exam.html', context)


@login_required
def end_current_exam(request):
    """End the current exam and clear current candidate"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'صيغة الطلب غير صحيحة'})

    try:
        import json
        data = json.loads(request.body)
        session_id = data.get('session_id')

        # Get the active session
        session = get_object_or_404(EvaluationSession, id=session_id, status='active')

        # Check if user has permission to end exam (examiner only)
        if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'examiner':
            return JsonResponse({'success': False, 'message': 'غير مسموح لك بهذا الإجراء'})

        # Clear the current candidate to end the exam
        session.current_candidate = None
        session.save()

        return JsonResponse({
            'success': True,
            'message': 'تم إنهاء الاختبار الحالي بنجاح'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        })


@login_required
def check_exam_status(request):
    """Check if there's an active exam for the examinee"""
    try:
        # Get active session with current candidate
        active_session = EvaluationSession.objects.filter(
            status='active'
        ).exclude(current_candidate__isnull=True).first()

        if active_session:
            return JsonResponse({
                'success': True,
                'exam_active': True,
                'candidate_name': active_session.current_candidate.student_name
            })
        else:
            return JsonResponse({
                'success': True,
                'exam_active': False,
                'message': 'لا يوجد اختبار نشط'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في التحقق من حالة الاختبار: {str(e)}'
        })


@login_required
def get_all_questions(request):
    """Get all active questions for committee members"""
    try:
        questions = EvaluationQuestion.objects.filter(is_active=True).values(
            'id', 'question_text', 'question_type'
        )

        return JsonResponse({
            'success': True,
            'questions': list(questions)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في تحميل الأسئلة: {str(e)}'
        })


@login_required
def get_plan_candidates(request):
    """Get all candidates for a specific plan"""
    try:
        plan_id = request.GET.get('plan_id')
        if not plan_id:
            return JsonResponse({
                'success': False,
                'message': 'معرف الخطة مطلوب'
            })

        plan = get_object_or_404(Plan, id=plan_id)
        candidates_data = []

        for candidate in plan.candidates.all():
            candidate_dict = {
                'id': candidate.id,
                'student_name': candidate.student_name,
                'birth_date': candidate.birth_date,
                'age': candidate.age,  # This uses the @property method
                'gender': candidate.gender,
                'primary_qualification': candidate.primary_qualification,
                'university': candidate.university,
                'phone_number': candidate.phone_number,
                'email': candidate.email
            }
            candidates_data.append(candidate_dict)

        return JsonResponse({
            'success': True,
            'plan_title': plan.title,
            'candidates': candidates_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في تحميل المرشحين: {str(e)}'
        })


@login_required
def get_current_question(request):
    """Get the current selected question with answer for committee members"""
    try:
        # Get the active session with current question
        active_session = EvaluationSession.objects.filter(
            status='active'
        ).select_related('current_question').first()

        if not active_session or not active_session.current_question:
            return JsonResponse({
                'success': False,
                'message': 'لا يوجد سؤال نشط حاليا'
            })

        question = active_session.current_question

        data = {
            'success': True,
            'question_id': question.id,
            'question_text': question.question_text,
            'question_type': question.question_type,
        }

        # Add options for MCQ questions
        if question.question_type == 'mcq':
            options = []
            if question.option_a: options.append(question.option_a)
            if question.option_b: options.append(question.option_b)
            if question.option_c: options.append(question.option_c)
            if question.option_d: options.append(question.option_d)
            data['options'] = options
            data['correct_answer'] = question.correct_answer

        # Add answer for qa and true_false questions
        if question.question_type in ['qa', 'true_false']:
            data['answer'] = question.answer

        # Add correct answer for true_false questions
        if question.question_type == 'true_false':
            data['correct_answer'] = question.correct_answer

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في تحميل السؤال: {str(e)}'
        })


@login_required
def get_evaluation_topics(request):
    """Get all active evaluation topics with their criteria"""
    try:
        from .models import EvaluationTopic

        topics = EvaluationTopic.objects.filter(
            is_active=True
        ).prefetch_related('criteria').order_by('order')

        topics_data = []
        for topic in topics:
            criteria_data = []
            for criteria in topic.criteria.all().order_by('order'):
                criteria_data.append({
                    'id': criteria.id,
                    'name': criteria.name,
                    'description': criteria.description,
                    'score_percentage': criteria.score_percentage,
                    'color': criteria.color,
                    'order': criteria.order
                })

            topics_data.append({
                'id': topic.id,
                'name': topic.name,
                'description': topic.description,
                'weight': topic.weight,
                'criteria': criteria_data
            })

        return JsonResponse({
            'success': True,
            'topics': topics_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في تحميل معايير التقييم: {str(e)}'
        })


@evaluator_required
def save_evaluation(request):
    """Save individual evaluation for current candidate"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        import json
        from .models import EvaluationTopic, EvaluationCriteria, CandidateTopicEvaluation

        data = json.loads(request.body)
        topic_id = data.get('topic_id')
        criteria_id = data.get('criteria_id')

        if not topic_id or not criteria_id:
            return JsonResponse({
                'success': False,
                'error': 'معرف المعيار والموضوع مطلوبان'
            }, status=400)

        # Get current active session and candidate
        active_session = EvaluationSession.objects.filter(
            status='active'
        ).select_related('current_candidate').first()

        if not active_session or not active_session.current_candidate:
            return JsonResponse({
                'success': False,
                'error': 'لا يوجد مرشح حالي للتقييم'
            }, status=400)

        # Validate topic and criteria exist
        try:
            topic = EvaluationTopic.objects.get(id=topic_id, is_active=True)
            criteria = EvaluationCriteria.objects.get(id=criteria_id, topic=topic)
        except (EvaluationTopic.DoesNotExist, EvaluationCriteria.DoesNotExist):
            return JsonResponse({
                'success': False,
                'error': 'المعيار أو الموضوع غير موجود'
            }, status=404)

        # Create or update evaluation
        evaluation, created = CandidateTopicEvaluation.objects.update_or_create(
            candidate=active_session.current_candidate,
            topic=topic,
            evaluator=request.user,
            defaults={
                'session': active_session,
                'criteria': criteria,
                'notes': '',
                'updated_at': timezone.now()
            }
        )

        return JsonResponse({
            'success': True,
            'message': 'تم حفظ التقييم بنجاح',
            'evaluation_id': evaluation.id,
            'created': created
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'صيغة البيانات غير صحيحة'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'خطأ في حفظ التقييم: {str(e)}'
        }, status=500)


@evaluator_required
def load_user_evaluations(request):
    """Load existing evaluations for current candidate by current user"""
    try:
        from .models import CandidateTopicEvaluation

        # Get current active session and candidate
        active_session = EvaluationSession.objects.filter(
            status='active'
        ).select_related('current_candidate').first()

        if not active_session or not active_session.current_candidate:
            return JsonResponse({
                'success': True,
                'evaluations': [],
                'message': 'لا يوجد مرشح حالي للتقييم'
            })

        # Get user's evaluations for current candidate
        evaluations = CandidateTopicEvaluation.objects.filter(
            candidate=active_session.current_candidate,
            evaluator=request.user
        ).select_related('topic', 'criteria').order_by('topic__order')

        evaluations_data = []
        for evaluation in evaluations:
            evaluations_data.append({
                'id': evaluation.id,
                'topic_id': evaluation.topic.id,
                'topic_name': evaluation.topic.name,
                'criteria_id': evaluation.criteria.id,
                'criteria_name': evaluation.criteria.name,
                'score': evaluation.criteria.score_percentage,
                'created_at': evaluation.created_at.isoformat(),
                'updated_at': evaluation.updated_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'evaluations': evaluations_data,
            'candidate_name': active_session.current_candidate.student_name
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'خطأ في تحميل التقييمات: {str(e)}'
        })


@evaluator_required
def get_evaluation_summary(request):
    """Get evaluation summary with totals for current candidate"""
    try:
        from .models import CandidateTopicEvaluation, EvaluationTopic
        from django.db.models import Sum, Count, Avg

        # Get current active session and candidate
        active_session = EvaluationSession.objects.filter(
            status='active'
        ).select_related('current_candidate').first()

        if not active_session or not active_session.current_candidate:
            return JsonResponse({
                'success': False,
                'error': 'لا يوجد مرشح حالي للتقييم'
            })

        candidate = active_session.current_candidate

        # Get all active topics for reference
        all_topics = EvaluationTopic.objects.filter(is_active=True).order_by('order')

        # Get all evaluations for this candidate (from all evaluators)
        all_evaluations = CandidateTopicEvaluation.objects.filter(
            candidate=candidate
        ).select_related('topic', 'criteria', 'evaluator', 'evaluator__profile')

        # Calculate totals by topic
        topic_totals = {}
        evaluator_totals = {}

        for evaluation in all_evaluations:
            topic_id = evaluation.topic.id
            evaluator_id = evaluation.evaluator.id

            # Initialize topic total if not exists
            if topic_id not in topic_totals:
                topic_totals[topic_id] = {
                    'topic_name': evaluation.topic.name,
                    'total_score': 0,
                    'evaluator_count': 0,
                    'weighted_score': 0,
                    'weight': evaluation.topic.weight,
                    'evaluations': {}
                }

            # Initialize evaluator total if not exists
            if evaluator_id not in evaluator_totals:
                evaluator_totals[evaluator_id] = {
                    'evaluator_name': evaluation.evaluator.get_full_name() or evaluation.evaluator.username,
                    'total_score': 0,
                    'topic_count': 0,
                    'weighted_total': 0
                }

            # Get the score from criteria
            score = evaluation.criteria.score_percentage

            # Store evaluation per evaluator (this will replace previous evaluation by same evaluator)
            topic_totals[topic_id]['evaluations'][evaluator_id] = score

        # Calculate totals and averages properly
        for topic_id in topic_totals:
            topic = topic_totals[topic_id]
            evaluations = topic['evaluations']

            if evaluations:
                # Calculate total and average from unique evaluator scores
                topic['total_score'] = sum(evaluations.values())
                topic['evaluator_count'] = len(evaluations)
                topic['average_score'] = topic['total_score'] / topic['evaluator_count']
                topic['weighted_score'] = topic['average_score'] * topic['weight']
            else:
                topic['total_score'] = 0
                topic['evaluator_count'] = 0
                topic['average_score'] = 0
                topic['weighted_score'] = 0

        # Calculate evaluator totals properly (avoiding double counting)
        for topic_id, topic_data in topic_totals.items():
            for evaluator_id, score in topic_data['evaluations'].items():
                topic_weight = topic_data['weight']
                evaluator_totals[evaluator_id]['total_score'] += score
                evaluator_totals[evaluator_id]['topic_count'] += 1
                evaluator_totals[evaluator_id]['weighted_total'] += (score * topic_weight)

        # Calculate overall totals
        total_possible_score = sum(topic.weight * 100 for topic in all_topics)
        total_weighted_score = sum(topic['weighted_score'] for topic in topic_totals.values())
        overall_percentage = (total_weighted_score / total_possible_score * 100) if total_possible_score > 0 else 0


        # Get current user's evaluation status
        user_evaluations = CandidateTopicEvaluation.objects.filter(
            candidate=candidate,
            evaluator=request.user
        ).values_list('topic_id', flat=True)

        completed_topics = len(user_evaluations)
        total_topics = all_topics.count()
        completion_percentage = (completed_topics / total_topics * 100) if total_topics > 0 else 0

        return JsonResponse({
            'success': True,
            'candidate_name': candidate.student_name,
            'topic_totals': topic_totals,
            'evaluator_totals': evaluator_totals,
            'overall_stats': {
                'total_weighted_score': total_weighted_score,
                'total_possible_score': total_possible_score,
                'overall_percentage': overall_percentage,
                'completed_topics': completed_topics,
                'total_topics': total_topics,
                'completion_percentage': completion_percentage
            },
            'user_evaluation_status': {
                'completed_topics': list(user_evaluations),
                'completion_rate': completion_percentage
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'خطأ في تحميل ملخص التقييم: {str(e)}'
        })


@evaluator_required
def save_complete_evaluation(request):
    """Save complete evaluation report for a candidate by the current evaluator"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'طريقة الطلب غير صحيحة'})

    try:
        from .models import CandidateTopicEvaluation, EvaluationTopic, EvaluationReport
        from django.db.models import Sum, Count, Avg
        import json

        # Get current active session and candidate
        active_session = EvaluationSession.objects.filter(
            status='active'
        ).select_related('current_candidate').first()

        if not active_session or not active_session.current_candidate:
            return JsonResponse({
                'success': False,
                'error': 'لا يوجد مرشح حالي للتقييم'
            })

        candidate = active_session.current_candidate
        evaluator = request.user

        # Check if user has completed all evaluations for all topics
        all_topics = EvaluationTopic.objects.filter(is_active=True)
        user_evaluations = CandidateTopicEvaluation.objects.filter(
            candidate=candidate,
            evaluator=evaluator
        )

        if user_evaluations.count() < all_topics.count():
            return JsonResponse({
                'success': False,
                'error': f'يجب إكمال تقييم جميع المحاور أولاً. تم تقييم {user_evaluations.count()} من أصل {all_topics.count()} محاور.'
            })

        # Get all evaluations for this candidate (from all evaluators)
        all_evaluations = CandidateTopicEvaluation.objects.filter(
            candidate=candidate
        ).select_related('topic', 'criteria', 'evaluator')

        # Calculate totals using same logic as get_evaluation_summary
        topic_totals = {}
        for evaluation in all_evaluations:
            topic_id = evaluation.topic.id
            evaluator_id = evaluation.evaluator.id

            if topic_id not in topic_totals:
                topic_totals[topic_id] = {
                    'topic_name': evaluation.topic.name,
                    'weight': evaluation.topic.weight,
                    'evaluations': {}
                }

            topic_totals[topic_id]['evaluations'][evaluator_id] = evaluation.criteria.score_percentage

        # Calculate final scores
        total_weighted_score = 0
        evaluation_data = {
            'topics': {},
            'user_evaluations': {},
            'summary': {}
        }

        for topic_id, topic_data in topic_totals.items():
            evaluations = topic_data['evaluations']
            if evaluations:
                total_score = sum(evaluations.values())
                evaluator_count = len(evaluations)
                average_score = total_score / evaluator_count
                weighted_score = average_score * topic_data['weight']
                total_weighted_score += weighted_score

                evaluation_data['topics'][topic_id] = {
                    'name': topic_data['topic_name'],
                    'weight': topic_data['weight'],
                    'average_score': average_score,
                    'weighted_score': weighted_score,
                    'evaluator_count': evaluator_count
                }

        # Store current user's specific evaluations
        for evaluation in user_evaluations:
            evaluation_data['user_evaluations'][evaluation.topic.id] = {
                'topic_name': evaluation.topic.name,
                'criteria_name': evaluation.criteria.name,
                'score_percentage': evaluation.criteria.score_percentage,
                'notes': evaluation.notes
            }

        # Calculate totals
        total_possible_score = sum(topic.weight * 100 for topic in all_topics)
        overall_percentage = (total_weighted_score / total_possible_score * 100) if total_possible_score > 0 else 0

        evaluation_data['summary'] = {
            'total_weighted_score': total_weighted_score,
            'total_possible_score': total_possible_score,
            'overall_percentage': overall_percentage,
            'total_topics': all_topics.count(),
            'completed_topics': user_evaluations.count()
        }

        # Get any additional notes from request
        general_notes = request.POST.get('general_notes', '')

        # Create or update the evaluation report
        report, created = EvaluationReport.objects.update_or_create(
            session=active_session,
            candidate=candidate,
            evaluator=evaluator,
            defaults={
                'total_weighted_score': total_weighted_score,
                'total_possible_score': total_possible_score,
                'overall_percentage': overall_percentage,
                'evaluation_data': evaluation_data,
                'general_notes': general_notes,
                'is_finalized': True
            }
        )

        action = 'تم إنشاء' if created else 'تم تحديث'

        return JsonResponse({
            'success': True,
            'message': f'{action} تقرير التقييم بنجاح',
            'report_id': report.id,
            'percentage': round(overall_percentage, 1),
            'grade': report.grade_text,
            'created': created
        })

    except Exception as e:
        import traceback
        print(f"Error in save_complete_evaluation: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'حدث خطأ في حفظ التقييم: {str(e)}'
        })


@evaluator_required
def get_candidate_details(request):
    """Get detailed candidate information for modal display"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'طريقة الطلب غير صحيحة'})

    try:
        from students.models import Person

        candidate_id = request.GET.get('candidate_id')
        if not candidate_id:
            return JsonResponse({
                'success': False,
                'error': 'معرف المرشح مطلوب'
            })

        candidate = get_object_or_404(Person, id=candidate_id)

        # Prepare candidate data
        candidate_data = {
            'id': candidate.id,
            'student_name': candidate.student_name,
            'birth_date': candidate.birth_date.strftime('%d/%m/%Y') if candidate.birth_date else None,
            'age': candidate.age,
            'gender': candidate.gender,
            'marital_status': candidate.marital_status,
            'number_of_children': candidate.number_of_children,
            'address': candidate.address,
            'phone_number': candidate.phone_number,
            'email': candidate.email,
            'primary_qualification': candidate.primary_qualification,
            'university': candidate.university,
            'general_degree': candidate.general_degree,
            'graduation_year': candidate.graduation_year,
            'application_date': candidate.application_date.strftime('%d/%m/%Y') if candidate.application_date else None,
            'application_status': candidate.get_application_status_display() if candidate.application_status else None,
            'profile_image_url': candidate.get_profile_image_url(),
        }

        return JsonResponse({
            'success': True,
            'candidate': candidate_data
        })

    except Exception as e:
        import traceback
        print(f"Error in get_candidate_details: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'حدث خطأ في تحميل بيانات المرشح: {str(e)}'
        })
