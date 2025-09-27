from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    # Examiner URLs
    path('examiner/', views.examiner_dashboard, name='examiner_dashboard'),
    path('examiner/sessions/', views.session_list, name='session_list'),
    path('examiner/plan-selection/', views.plan_selection, name='plan_selection'),
    path('examiner/session/create/', views.session_create, name='session_create'),
    path('examiner/session/create/<int:plan_id>/', views.session_create_for_plan, name='session_create_for_plan'),
    path('examiner/session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('examiner/session/<int:session_id>/start/', views.session_start, name='session_start'),
    path('examiner/session/<int:session_id>/pause/', views.session_pause, name='session_pause'),
    path('examiner/session/<int:session_id>/resume/', views.session_resume, name='session_resume'),
    path('examiner/session/<int:session_id>/complete/', views.session_complete, name='session_complete'),
    path('examiner/session/<int:session_id>/next-candidate/', views.next_candidate, name='next_candidate'),
    path('examiner/session/<int:session_id>/set-candidate/', views.set_current_candidate, name='set_current_candidate'),

    # Committee Member URLs
    path('committee/', views.committee_dashboard, name='committee_dashboard'),
    path('committee/evaluate/<int:evaluation_id>/', views.candidate_evaluate, name='candidate_evaluate'),
    path('committee/evaluate/create/', views.create_evaluation, name='create_evaluation'),
    path('committee/current-candidate/', views.current_candidate_view, name='committee_current_candidate'),
    path('committee/exam/', views.committee_exam, name='committee_exam'),

    # Question Management URLs
    path('questions/', views.question_list, name='question_list'),
    path('questions/create/', views.question_create, name='question_create'),
    path('questions/<int:question_id>/', views.question_detail, name='question_detail'),
    path('questions/<int:question_id>/update/', views.question_update, name='question_update'),
    path('questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),

    # Examinee URLs
    path('examinee/', views.examinee_dashboard, name='examinee_dashboard'),
    path('examinee/exam/', views.examinee_exam, name='examinee_exam'),

    # AJAX URLs
    path('ajax/session-status/<int:session_id>/', views.ajax_session_status, name='ajax_session_status'),
    path('ajax/current-candidate/', views.ajax_current_candidate, name='ajax_current_candidate'),
    path('ajax/random-qa-question/', views.get_random_qa_question, name='ajax_random_qa_question'),
    path('ajax/qa-question/<int:question_id>/', views.get_qa_question_with_answer, name='ajax_qa_question_with_answer'),
    path('ajax/end-current-exam/', views.end_current_exam, name='ajax_end_current_exam'),
    path('ajax/check-exam-status/', views.check_exam_status, name='ajax_check_exam_status'),
    path('ajax/get-all-questions/', views.get_all_questions, name='ajax_get_all_questions'),
    path('ajax/get-plan-candidates/', views.get_plan_candidates, name='ajax_get_plan_candidates'),
    path('ajax/get-current-question/', views.get_current_question, name='ajax_get_current_question'),
    path('ajax/get-evaluation-topics/', views.get_evaluation_topics, name='ajax_get_evaluation_topics'),
    path('ajax/save-evaluation/', views.save_evaluation, name='ajax_save_evaluation'),
    path('ajax/load-user-evaluations/', views.load_user_evaluations, name='ajax_load_user_evaluations'),
    path('ajax/get-evaluation-summary/', views.get_evaluation_summary, name='ajax_get_evaluation_summary'),
    path('ajax/save-complete-evaluation/', views.save_complete_evaluation, name='ajax_save_complete_evaluation'),
    path('ajax/get-candidate-details/', views.get_candidate_details, name='ajax_get_candidate_details'),
]