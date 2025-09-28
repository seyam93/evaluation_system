from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from accounts.decorators import candidate_manager_required, committee_required
import csv
import openpyxl
import logging
from datetime import date
from .models import Person, Qualification, Experience, Plan
from .forms import PersonForm, QualificationForm, ExperienceForm, CandidateSearchForm, BulkActionForm, PlanForm, PlanSelectionForm, PreviousTestForm

logger = logging.getLogger(__name__)


@committee_required
def candidate_list(request):
    """List all candidates grouped by recruitment plans"""
    # Check if filtering by specific plan
    plan_id = request.GET.get('plan')

    if plan_id:
        # Show candidates for specific plan
        plan = get_object_or_404(Plan, id=plan_id)
        candidates = plan.candidates.all().order_by('-created_at')

        # Pagination for single plan view
        paginator = Paginator(candidates, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'single_plan_view': True,
            'plan': plan,
            'candidates': page_obj,
            'total_candidates': candidates.count(),
        }
    else:
        # Show all plans with their candidates
        plans = Plan.objects.filter(is_active=True).order_by('-created_at')

        plans_with_candidates = []
        total_candidates = 0

        for plan in plans:
            candidates = plan.candidates.all().order_by('-created_at')
            plans_with_candidates.append({
                'plan': plan,
                'candidates': candidates
            })
            total_candidates += candidates.count()

        context = {
            'single_plan_view': False,
            'plans_with_candidates': plans_with_candidates,
            'total_candidates': total_candidates,
            'plans_count': plans.count(),
        }

    return render(request, 'students/candidate_list.html', context)


@committee_required
def candidate_detail(request, pk):
    """Detailed view of a candidate"""
    candidate = get_object_or_404(Person, pk=pk)
    qualifications = candidate.qualifications.all()
    experiences = candidate.experiences.all()

    context = {
        'candidate': candidate,
        'qualifications': qualifications,
        'experiences': experiences,
        'can_manage': request.user.profile.can_manage_candidates if hasattr(request.user, 'profile') else False,
    }

    return render(request, 'students/candidate_detail.html', context)


@candidate_manager_required
def candidate_create(request):
    """Create a new candidate"""
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        previous_test_form = PreviousTestForm(request.POST)

        if form.is_valid() and previous_test_form.is_valid():
            try:
                candidate = form.save()
                logger.info(f"New candidate created: {candidate.student_name} (ID: {candidate.id})")

                # Handle previous tests
                from examinations.models import CandidateTest, TestCategory
                test_data = previous_test_form.get_test_data()

                for test_info in test_data:
                    # Get or create test category
                    test_category, created = TestCategory.objects.get_or_create(
                        name=test_info['name'],
                        examination_type='previous_test',
                        defaults={
                            'max_score': test_info['max_score'],
                            'description': f'Previous test for {test_info["name_arabic"]}',
                            'result_type': test_info['result_type']
                        }
                    )

                    # Update the test category if it already exists but result_type differs
                    if not created and test_category.result_type != test_info['result_type']:
                        test_category.result_type = test_info['result_type']
                        test_category.save()

                    # Create the test result based on result type
                    test_result_data = {
                        'person': candidate,
                        'test_category': test_category,
                        'max_possible_score': test_info['max_score'],
                        'is_previous_test': True,
                        'notes': f'Previous test result entered during registration'
                    }

                    if test_info['result_type'] == 'pass_fail':
                        test_result_data['pass_fail_result'] = test_info['pass_fail_result']
                        test_result_data['score'] = None
                    else:
                        test_result_data['score'] = test_info['score']
                        test_result_data['pass_fail_result'] = None

                    CandidateTest.objects.create(**test_result_data)
                    logger.info(f"Created test result for {candidate.student_name} - {test_category.name}: {test_info['score'] if test_info['result_type'] == 'numerical' else test_info['pass_fail_result']}")

                # Handle qualifications
                qualification_names = []
                qualification_dates = []
                for key, value in request.POST.items():
                    if key.startswith('qualification_name_') and value:
                        qualification_names.append(value)
                    elif key.startswith('qualification_date_') and value:
                        qualification_dates.append(value)

                # Create qualification objects
                for i, name in enumerate(qualification_names):
                    if i < len(qualification_dates):
                        Qualification.objects.create(
                            person=candidate,
                            degree_name=name,
                            degree_date=qualification_dates[i] if qualification_dates[i] else None
                        )
                    else:
                        Qualification.objects.create(
                            person=candidate,
                            degree_name=name
                        )

                # Handle experiences
                job_titles = []
                company_names = []
                start_dates = []
                end_dates = []

                for key, value in request.POST.items():
                    if key.startswith('job_title_') and value:
                        job_titles.append(value)
                    elif key.startswith('company_name_') and value:
                        company_names.append(value)
                    elif key.startswith('start_date_') and value:
                        start_dates.append(value)
                    elif key.startswith('end_date_') and value:
                        end_dates.append(value)

                # Create experience objects
                for i, title in enumerate(job_titles):
                    company = company_names[i] if i < len(company_names) else None
                    start_date = start_dates[i] if i < len(start_dates) else None
                    end_date = end_dates[i] if i < len(end_dates) else None

                    Experience.objects.create(
                        person=candidate,
                        job_title=title,
                        company_name=company,
                        start_date=start_date if start_date else None,
                        end_date=end_date if end_date else None
                    )

                logger.info(f"Added {len(qualification_names)} qualifications and {len(job_titles)} experiences for {candidate.student_name}")

                # Update test summary if previous tests were added
                if test_data:
                    from examinations.models import CandidateTestSummary
                    summary, created = CandidateTestSummary.objects.get_or_create(person=candidate)
                    summary.update_summary()

                messages.success(request, f'تم إنشاء ملف المرشح "{candidate.student_name}" بنجاح مع جميع المؤهلات والخبرات والاختبارات السابقة.')
                return redirect('students:candidate_detail', pk=candidate.pk)
            except Exception as e:
                logger.error(f"Error creating candidate: {str(e)}", exc_info=True)
                messages.error(request, 'حدث خطأ أثناء إنشاء ملف المرشح. يرجى المحاولة مرة أخرى.')
    else:
        form = PersonForm()
        previous_test_form = PreviousTestForm()

    context = {
        'form': form,
        'previous_test_form': previous_test_form,
        'title': 'إضافة مرشح جديد',
        'submit_text': 'إنشاء المرشح'
    }

    return render(request, 'students/candidate_form.html', context)


@candidate_manager_required
def candidate_update(request, pk):
    """Update an existing candidate"""
    candidate = get_object_or_404(Person, pk=pk)

    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES, instance=candidate)
        previous_test_form = PreviousTestForm(request.POST)

        if form.is_valid() and previous_test_form.is_valid():
            candidate = form.save()

            # Handle previous tests updates
            from examinations.models import CandidateTest, TestCategory
            test_data = previous_test_form.get_test_data()

            # Remove existing previous tests to update them
            CandidateTest.objects.filter(person=candidate, is_previous_test=True).delete()

            # Add new/updated previous tests
            for test_info in test_data:
                # Get or create test category
                test_category, created = TestCategory.objects.get_or_create(
                    name=test_info['name'],
                    examination_type='previous_test',
                    defaults={
                        'max_score': test_info['max_score'],
                        'description': f'Previous test for {test_info["name_arabic"]}',
                        'result_type': test_info['result_type']
                    }
                )

                # Update the test category if it already exists but result_type differs
                if not created and test_category.result_type != test_info['result_type']:
                    test_category.result_type = test_info['result_type']
                    test_category.save()

                # Create the test result based on result type
                test_result_data = {
                    'person': candidate,
                    'test_category': test_category,
                    'max_possible_score': test_info['max_score'],
                    'is_previous_test': True,
                    'notes': f'Previous test result updated'
                }

                if test_info['result_type'] == 'pass_fail':
                    test_result_data['pass_fail_result'] = test_info['pass_fail_result']
                    test_result_data['score'] = None
                else:
                    test_result_data['score'] = test_info['score']
                    test_result_data['pass_fail_result'] = None

                CandidateTest.objects.create(**test_result_data)

            # Update test summary if previous tests were modified
            from examinations.models import CandidateTestSummary
            summary, created = CandidateTestSummary.objects.get_or_create(person=candidate)
            summary.update_summary()

            messages.success(request, f'تم تحديث ملف المرشح "{candidate.student_name}" بنجاح.')
            return redirect('students:candidate_detail', pk=candidate.pk)
    else:
        form = PersonForm(instance=candidate)

        # Pre-populate previous test form with existing data
        from examinations.models import get_previous_tests_for_person, PreviousTestTemplate
        existing_tests = get_previous_tests_for_person(candidate)

        initial_data = {}
        # Create a mapping from test category name to template ID
        templates = PreviousTestTemplate.objects.filter(is_active=True)
        name_to_template = {template.name: template for template in templates}

        for test in existing_tests:
            # Find the corresponding template
            template = name_to_template.get(test.test_category.name)
            if template:
                field_name = f'test_{template.id}'
                if template.result_type == 'pass_fail':
                    initial_data[field_name] = test.pass_fail_result
                else:
                    initial_data[field_name] = test.score

        previous_test_form = PreviousTestForm(initial=initial_data)

    context = {
        'form': form,
        'previous_test_form': previous_test_form,
        'candidate': candidate,
        'title': f'تعديل {candidate.student_name}',
        'submit_text': 'تحديث المرشح',
        'is_update': True
    }

    return render(request, 'students/candidate_form.html', context)


@candidate_manager_required
@require_http_methods(["POST"])
def candidate_delete(request, pk):
    """Delete a candidate"""
    candidate = get_object_or_404(Person, pk=pk)
    candidate_name = candidate.student_name
    candidate.delete()
    messages.success(request, f'Candidate "{candidate_name}" has been deleted successfully.')
    return redirect('students:candidate_list')


@candidate_manager_required
def qualification_create(request, candidate_pk):
    """Add a qualification to a candidate"""
    candidate = get_object_or_404(Person, pk=candidate_pk)

    if request.method == 'POST':
        form = QualificationForm(request.POST)
        if form.is_valid():
            qualification = form.save(commit=False)
            qualification.person = candidate
            qualification.save()
            messages.success(request, 'Qualification added successfully.')
            return redirect('students:candidate_detail', pk=candidate.pk)
    else:
        form = QualificationForm(initial={'person': candidate})

    context = {
        'form': form,
        'candidate': candidate,
        'title': f'Add Qualification for {candidate.student_name}',
        'submit_text': 'Add Qualification'
    }

    return render(request, 'students/qualification_form.html', context)


@candidate_manager_required
def experience_create(request, candidate_pk):
    """Add an experience to a candidate"""
    candidate = get_object_or_404(Person, pk=candidate_pk)

    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.person = candidate
            experience.save()
            messages.success(request, 'Experience added successfully.')
            return redirect('students:candidate_detail', pk=candidate.pk)
    else:
        form = ExperienceForm(initial={'person': candidate})

    context = {
        'form': form,
        'candidate': candidate,
        'title': f'Add Experience for {candidate.student_name}',
        'submit_text': 'Add Experience'
    }

    return render(request, 'students/experience_form.html', context)


@candidate_manager_required
def bulk_actions(request):
    """Handle bulk actions for candidates"""
    if request.method == 'POST':
        form = BulkActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            selected_ids = request.POST.getlist('selected_candidates')

            if not selected_ids:
                messages.error(request, 'No candidates selected.')
                return redirect('students:candidate_list')

            candidates = Person.objects.filter(id__in=selected_ids)

            if action == 'export_csv':
                return export_candidates_csv(candidates)
            elif action == 'export_excel':
                return export_candidates_excel(candidates)
            elif action == 'delete':
                count = candidates.count()
                candidates.delete()
                messages.success(request, f'{count} candidates deleted successfully.')
                return redirect('students:candidate_list')

    return redirect('students:candidate_list')


def export_candidates_csv(candidates):
    """Export candidates to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="candidates.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Email', 'Phone', 'Birth Date', 'Age', 'Gender',
        'Primary Qualification', 'University', 'General Degree',
        'Graduation Year', 'Marital Status', 'Children', 'Address'
    ])

    for candidate in candidates:
        writer.writerow([
            candidate.student_name,
            candidate.email,
            candidate.phone_number,
            candidate.birth_date,
            candidate.age,
            candidate.gender,
            candidate.primary_qualification,
            candidate.university,
            candidate.general_degree,
            candidate.graduation_year,
            candidate.marital_status,
            candidate.number_of_children,
            candidate.address
        ])

    return response


def export_candidates_excel(candidates):
    """Export candidates to Excel"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="candidates.xlsx"'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Candidates'

    # Headers
    headers = [
        'Name', 'Email', 'Phone', 'Birth Date', 'Age', 'Gender',
        'Primary Qualification', 'University', 'General Degree',
        'Graduation Year', 'Marital Status', 'Children', 'Address'
    ]
    worksheet.append(headers)

    # Data
    for candidate in candidates:
        worksheet.append([
            candidate.student_name,
            candidate.email,
            candidate.phone_number,
            candidate.birth_date,
            candidate.age,
            candidate.gender,
            candidate.primary_qualification,
            candidate.university,
            candidate.general_degree,
            candidate.graduation_year,
            candidate.marital_status,
            candidate.number_of_children,
            candidate.address
        ])

    workbook.save(response)
    return response


@committee_required
def candidate_search_api(request):
    """API endpoint for candidate search autocomplete"""
    query = request.GET.get('q', '')
    candidates = Person.objects.filter(
        Q(student_name__icontains=query) |
        Q(email__icontains=query)
    )[:10]

    results = [
        {
            'id': c.id,
            'name': c.student_name,
            'email': c.email,
            'university': c.university
        }
        for c in candidates
    ]

    return JsonResponse({'results': results})


# ==================== PLAN MANAGEMENT VIEWS ====================

@candidate_manager_required
def plan_list(request):
    """List all recruitment plans"""
    plans = Plan.objects.all().order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        is_active = status_filter == 'active'
        plans = plans.filter(is_active=is_active)

    context = {
        'plans': plans,
        'status_choices': [('active', 'نشطة'), ('inactive', 'غير نشطة')],
        'current_status': status_filter,
        'can_manage': request.user.profile.can_manage_candidates if hasattr(request.user, 'profile') else False,
    }

    return render(request, 'students/plan_list.html', context)


@candidate_manager_required
def plan_detail(request, pk):
    """Detailed view of a recruitment plan with its candidates"""
    plan = get_object_or_404(Plan, pk=pk)
    candidates = plan.candidates.all().order_by('-application_date')

    # Pagination for candidates
    paginator = Paginator(candidates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'plan': plan,
        'candidates': page_obj,
        'total_candidates': candidates.count(),
        'can_manage': request.user.profile.can_manage_candidates if hasattr(request.user, 'profile') else False,
    }

    return render(request, 'students/plan_detail.html', context)


@candidate_manager_required
def plan_create(request):
    """Create a new recruitment plan"""
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Recruitment plan "{plan.title}" has been created successfully.')
            return redirect('students:plan_detail', pk=plan.pk)
    else:
        form = PlanForm()

    context = {
        'form': form,
        'title': 'Create New Recruitment Plan',
        'submit_text': 'Create Plan'
    }

    return render(request, 'students/plan_form.html', context)


@candidate_manager_required
def plan_update(request, pk):
    """Update an existing recruitment plan"""
    plan = get_object_or_404(Plan, pk=pk)

    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan "{plan.title}" has been updated successfully.')
            return redirect('students:plan_detail', pk=plan.pk)
    else:
        form = PlanForm(instance=plan)

    context = {
        'form': form,
        'plan': plan,
        'title': f'Edit {plan.title}',
        'submit_text': 'Update Plan'
    }

    return render(request, 'students/plan_form.html', context)


@candidate_manager_required
@require_http_methods(["POST"])
def plan_delete(request, pk):
    """Delete a recruitment plan"""
    plan = get_object_or_404(Plan, pk=pk)
    plan_title = plan.title
    plan.delete()
    messages.success(request, f'Plan "{plan_title}" has been deleted successfully.')
    return redirect('students:plan_list')


@candidate_manager_required


@committee_required
def plan_selection_for_evaluation(request):
    """Select a recruitment plan for evaluation"""
    if request.method == 'POST':
        form = PlanSelectionForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data['plan']
            # Redirect to evaluation interface with selected plan
            return redirect('students:plan_evaluation', pk=plan.pk)
    else:
        form = PlanSelectionForm()

    context = {
        'form': form,
        'title': 'Select Recruitment Plan for Evaluation',
        'submit_text': 'Start Evaluation'
    }

    return render(request, 'students/plan_selection.html', context)


@committee_required
def plan_evaluation(request, pk):
    """Evaluation interface for a specific recruitment plan"""
    plan = get_object_or_404(Plan, pk=pk)
    candidates = plan.candidates.all().order_by('student_name')

    # Filter candidates by application status if needed
    status_filter = request.GET.get('status')
    if status_filter:
        candidates = candidates.filter(application_status=status_filter)

    context = {
        'plan': plan,
        'candidates': candidates,
        'status_choices': Person.APPLICATION_STATUS_CHOICES,
        'current_status': status_filter,
        'can_evaluate': request.user.profile.can_evaluate_candidates if hasattr(request.user, 'profile') else False,
    }

    return render(request, 'students/plan_evaluation.html', context)
