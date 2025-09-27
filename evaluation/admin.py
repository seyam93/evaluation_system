from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    EvaluationSession, EvaluationQuestion, CandidateEvaluation,
    EvaluationAnswer, EvaluationTemplate, EvaluationTopic,
    EvaluationCriteria, CandidateTopicEvaluation, EvaluationReport
)


@admin.register(EvaluationQuestion)
class EvaluationQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'question_type', 'is_active', 'created_at']
    list_filter = ['question_type', 'is_active', 'created_at']
    search_fields = ['question_text', 'answer']
    list_editable = ['is_active']
    ordering = ['-created_at']

    fieldsets = (
        ('معلومات السؤال', {
            'fields': ('question_text', 'question_type', 'is_active')
        }),
        ('إجابة السؤال والجواب', {
            'fields': ('answer',),
            'classes': ('collapse',),
            'description': 'للأسئلة من نوع سؤال وجواب فقط'
        }),
        ('خيارات الاختيار من متعدد', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
            'classes': ('collapse',),
            'description': 'للأسئلة من نوع اختيار من متعدد فقط'
        }),
        ('الإجابة الصحيحة', {
            'fields': ('correct_answer',),
            'description': 'للاختيار من متعدد: A, B, C, D | للصح والخطأ: True, False'
        }),
    )

    def question_preview(self, obj):
        return obj.question_text[:100] + '...' if len(obj.question_text) > 100 else obj.question_text
    question_preview.short_description = 'نص السؤال'


@admin.register(EvaluationTemplate)
class EvaluationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'questions_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['questions']

    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = 'عدد الأسئلة'


class CandidateEvaluationInline(admin.TabularInline):
    model = CandidateEvaluation
    extra = 0
    readonly_fields = ['start_time', 'end_time', 'total_score', 'score_percentage']
    fields = ['candidate', 'evaluator', 'is_completed', 'total_score', 'score_percentage', 'recommendation']


@admin.register(EvaluationSession)
class EvaluationSessionAdmin(admin.ModelAdmin):
    list_display = [
        'plan_title', 'session_date', 'examiner', 'status',
        'progress_info', 'current_candidate_name', 'session_duration'
    ]
    list_filter = ['status', 'session_date', 'examiner']
    search_fields = ['plan__title', 'examiner__username', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage', 'session_duration']

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('plan', 'session_date', 'examiner')
        }),
        ('حالة الجلسة', {
            'fields': ('status', 'current_candidate', 'start_time', 'end_time')
        }),
        ('إحصائيات', {
            'fields': ('progress_percentage', 'session_duration'),
            'classes': ('collapse',)
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('تواريخ النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [CandidateEvaluationInline]

    def plan_title(self, obj):
        return obj.plan.title
    plan_title.short_description = 'خطة التوظيف'

    def progress_info(self, obj):
        progress = obj.progress_percentage
        evaluated = obj.evaluated_candidates_count
        total = obj.total_candidates

        if progress >= 75:
            color = 'green'
        elif progress >= 50:
            color = 'orange'
        else:
            color = 'red'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}% ({}/{})</span>',
            color, progress, evaluated, total
        )
    progress_info.short_description = 'التقدم'

    def current_candidate_name(self, obj):
        if obj.current_candidate:
            return obj.current_candidate.student_name
        return '-'
    current_candidate_name.short_description = 'المرشح الحالي'

    def session_duration(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            hours = duration.total_seconds() / 3600
            return f'{round(hours, 1)} ساعة'
        elif obj.start_time:
            return 'جارية'
        return '-'
    session_duration.short_description = 'مدة الجلسة'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('plan', 'examiner', 'current_candidate')


class EvaluationAnswerInline(admin.TabularInline):
    model = EvaluationAnswer
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['question', 'score', 'text_answer', 'notes']


@admin.register(CandidateEvaluation)
class CandidateEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_name', 'session_plan', 'evaluator', 'score_display',
        'recommendation', 'is_completed', 'evaluation_date'
    ]
    list_filter = ['is_completed', 'recommendation', 'start_time', 'session__plan']
    search_fields = ['candidate__student_name', 'evaluator__username', 'evaluator__first_name', 'evaluator__last_name', 'general_notes']
    readonly_fields = [
        'start_time', 'end_time', 'total_score', 'max_possible_score',
        'score_percentage', 'duration_minutes'
    ]

    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('session', 'candidate', 'evaluator')
        }),
        ('النتائج', {
            'fields': ('total_score', 'max_possible_score', 'score_percentage', 'recommendation')
        }),
        ('التوقيت', {
            'fields': ('start_time', 'end_time', 'duration_minutes', 'is_completed'),
            'classes': ('collapse',)
        }),
        ('ملاحظات', {
            'fields': ('general_notes',),
            'classes': ('collapse',)
        })
    )

    inlines = [EvaluationAnswerInline]

    def candidate_name(self, obj):
        return obj.candidate.student_name
    candidate_name.short_description = 'المرشح'

    def session_plan(self, obj):
        return obj.session.plan.title
    session_plan.short_description = 'الخطة'

    def score_display(self, obj):
        if obj.max_possible_score > 0:
            percentage = obj.score_percentage
            if percentage >= 85:
                color = 'green'
            elif percentage >= 70:
                color = 'orange'
            else:
                color = 'red'

            return format_html(
                '<span style="color: {}; font-weight: bold;">{}/{} ({}%)</span>',
                color, round(obj.total_score, 1), round(obj.max_possible_score, 1), round(percentage)
            )
        return str(round(obj.total_score, 1))
    score_display.short_description = 'النتيجة'

    def evaluation_date(self, obj):
        return obj.start_time.date() if obj.start_time else '-'
    evaluation_date.short_description = 'تاريخ التقييم'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate', 'session__plan', 'evaluator'
        )


@admin.register(EvaluationAnswer)
class EvaluationAnswerAdmin(admin.ModelAdmin):
    list_display = ['evaluation_candidate', 'question_title', 'score_display', 'created_at']
    list_filter = ['question__question_type', 'created_at', 'evaluation__session__plan']
    search_fields = ['evaluation__candidate__student_name', 'question__title', 'text_answer']
    readonly_fields = ['created_at', 'updated_at']

    def evaluation_candidate(self, obj):
        return f'{obj.evaluation.candidate.student_name} - {obj.evaluation.session.session_date}'
    evaluation_candidate.short_description = 'المرشح والجلسة'

    def question_title(self, obj):
        return obj.question.title
    question_title.short_description = 'السؤال'

    def score_display(self, obj):
        max_score = obj.question.max_score
        percentage = (obj.score / max_score) * 100 if max_score > 0 else 0

        if percentage >= 85:
            color = 'green'
        elif percentage >= 70:
            color = 'orange'
        else:
            color = 'red'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/{} ({}%)</span>',
            color, obj.score, max_score, round(percentage)
        )
    score_display.short_description = 'النتيجة'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'evaluation__candidate', 'evaluation__session', 'question'
        )


class EvaluationCriteriaInline(admin.TabularInline):
    model = EvaluationCriteria
    extra = 0
    fields = ['name', 'calculated_percentage', 'order', 'color', 'description']
    readonly_fields = ['calculated_percentage']
    ordering = ['order']

    def calculated_percentage(self, obj):
        if obj.pk:
            return f"{obj.score_percentage:.1f}%"
        return "سيتم حسابها تلقائياً"
    calculated_percentage.short_description = 'النسبة المحسوبة (%)'


@admin.register(EvaluationTopic)
class EvaluationTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight', 'criteria_count', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['weight', 'is_active', 'order']
    ordering = ['order']

    fieldsets = (
        ('معلومات المحور', {
            'fields': ('name', 'description', 'weight', 'is_active', 'order')
        }),
    )

    inlines = [EvaluationCriteriaInline]

    def criteria_count(self, obj):
        return obj.criteria.count()
    criteria_count.short_description = 'عدد المعايير'


@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    list_display = ['topic_name', 'name', 'calculated_percentage', 'order', 'color_display']
    list_filter = ['topic']
    search_fields = ['name', 'topic__name', 'description']
    list_editable = ['order']
    ordering = ['topic', 'order']

    def calculated_percentage(self, obj):
        return f"{obj.score_percentage:.1f}%"
    calculated_percentage.short_description = 'النسبة المحسوبة (%)'

    def topic_name(self, obj):
        return obj.topic.name
    topic_name.short_description = 'المحور'

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'اللون'


@admin.register(CandidateTopicEvaluation)
class CandidateTopicEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_name', 'topic_name', 'criteria_name',
        'score_display', 'evaluator', 'evaluation_date'
    ]
    list_filter = ['topic', 'criteria', 'session__plan', 'created_at']
    search_fields = ['candidate__student_name', 'evaluator__username', 'evaluator__first_name', 'evaluator__last_name', 'notes']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('session', 'candidate', 'evaluator', 'topic', 'criteria')
        }),
        ('النتيجة', {
            'fields': ('score_percentage',),
            'classes': ('collapse',)
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('تواريخ النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def candidate_name(self, obj):
        return obj.candidate.student_name
    candidate_name.short_description = 'المرشح'

    def topic_name(self, obj):
        return obj.topic.name
    topic_name.short_description = 'المحور'

    def criteria_name(self, obj):
        return obj.criteria.name
    criteria_name.short_description = 'المعيار'

    def score_display(self, obj):
        percentage = obj.score_percentage
        color = '#28a745' if percentage >= 75 else '#ffc107' if percentage >= 50 else '#dc3545'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}%</span>',
            color, percentage
        )
    score_display.short_description = 'النسبة'

    def evaluation_date(self, obj):
        return obj.created_at.date()
    evaluation_date.short_description = 'تاريخ التقييم'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate', 'topic', 'criteria', 'evaluator', 'session'
        )


@admin.register(EvaluationReport)
class EvaluationReportAdmin(admin.ModelAdmin):
    list_display = [
        'candidate_name', 'session_plan', 'evaluator_name', 'percentage_display',
        'grade_display', 'is_finalized', 'created_at'
    ]
    list_filter = ['is_finalized', 'session__plan', 'created_at']
    search_fields = ['candidate__student_name', 'evaluator__username', 'evaluator__first_name', 'evaluator__last_name', 'general_notes']
    readonly_fields = [
        'total_weighted_score', 'total_possible_score', 'overall_percentage',
        'created_at', 'updated_at', 'evaluation_data_display'
    ]

    fieldsets = (
        ('معلومات التقرير', {
            'fields': ('session', 'candidate', 'evaluator', 'is_finalized')
        }),
        ('النتائج الإجمالية', {
            'fields': ('total_weighted_score', 'total_possible_score', 'overall_percentage'),
            'description': 'النتائج المحسوبة من تقييمات جميع المقيمين'
        }),
        ('تفاصيل التقييم', {
            'fields': ('evaluation_data_display',),
            'description': 'التقييمات التفصيلية لكل محور مع النتائج المرجحة'
        }),
        ('ملاحظات إضافية', {
            'fields': ('general_notes',),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def candidate_name(self, obj):
        return obj.candidate.student_name
    candidate_name.short_description = 'المرشح'

    def session_plan(self, obj):
        return obj.session.plan.title
    session_plan.short_description = 'الخطة'

    def evaluator_name(self, obj):
        full_name = obj.evaluator.get_full_name()
        if full_name:
            return full_name
        return obj.evaluator.username
    evaluator_name.short_description = 'المقيم'

    def percentage_display(self, obj):
        percentage = obj.overall_percentage
        color = '#28a745' if percentage >= 85 else '#17a2b8' if percentage >= 75 else '#ffc107' if percentage >= 60 else '#dc3545'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{}%</span>',
            color, round(percentage, 1)
        )
    percentage_display.short_description = 'النسبة المئوية'

    def grade_display(self, obj):
        grade = obj.grade_text
        color = obj.grade_color

        colors = {
            'success': '#28a745',
            'info': '#17a2b8',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }

        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{}</span>',
            colors.get(color, '#6c757d'), grade
        )
    grade_display.short_description = 'التقدير'

    def evaluation_data_display(self, obj):
        if not obj.evaluation_data:
            return '-'

        data = obj.evaluation_data
        html = '<div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.4;">'

        # User evaluations section - more prominent
        if 'user_evaluations' in data:
            html += '<div style="margin-bottom: 15px;">'
            html += '<strong style="color: #2c3e50; font-size: 14px;">تقييمات المحاور:</strong><br>'
            for topic_id, eval_data in data['user_evaluations'].items():
                topic_name = eval_data.get("topic_name", "")
                criteria_name = eval_data.get("criteria_name", "")
                score = eval_data.get("score_percentage", 0)

                # Color coding based on score
                if score >= 75:
                    color = '#27ae60'  # green
                elif score >= 50:
                    color = '#f39c12'  # orange
                else:
                    color = '#e74c3c'  # red

                html += f'<div style="margin: 5px 0; padding: 5px; background: #f8f9fa; border-left: 3px solid {color};">'
                html += f'<strong>{topic_name}:</strong> {criteria_name} '
                html += f'<span style="color: {color}; font-weight: bold;">({score}%)</span>'
                html += '</div>'
            html += '</div>'

        # Summary section
        if 'summary' in data:
            summary = data['summary']
            html += '<div style="background: #ecf0f1; padding: 8px; border-radius: 4px; margin-top: 10px;">'
            html += f'<strong style="color: #34495e;">الملخص:</strong><br>'
            html += f'<span style="color: #7f8c8d;">المجموع المرجح:</span> <strong>{summary.get("total_weighted_score", 0):.1f}</strong><br>'
            html += f'<span style="color: #7f8c8d;">المجموع الأقصى:</span> <strong>{summary.get("total_possible_score", 0):.1f}</strong><br>'
            html += f'<span style="color: #7f8c8d;">النسبة المئوية:</span> <strong style="color: #e67e22;">{summary.get("overall_percentage", 0):.1f}%</strong>'
            html += '</div>'

        html += '</div>'
        return mark_safe(html)
    evaluation_data_display.short_description = 'تفاصيل التقييم'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'candidate', 'session__plan', 'evaluator'
        )
