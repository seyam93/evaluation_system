from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from students.models import Plan, Person


class EvaluationSession(models.Model):
    """Main evaluation session for a specific recruitment plan"""

    SESSION_STATUS = [
        ('setup', 'إعداد'),
        ('active', 'نشطة'),
        ('paused', 'متوقفة'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغية'),
    ]

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='evaluation_sessions',
        verbose_name='خطة التوظيف'
    )

    session_date = models.DateField(
        default=timezone.now,
        verbose_name='تاريخ الجلسة'
    )

    examiner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='examination_sessions',
        verbose_name='المشرف على الاختبار'
    )

    current_candidate = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_evaluation_sessions',
        verbose_name='المرشح الحالي'
    )

    current_question = models.ForeignKey(
        'EvaluationQuestion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_sessions',
        verbose_name='السؤال الحالي'
    )

    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS,
        default='setup',
        verbose_name='حالة الجلسة'
    )

    start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت البداية'
    )

    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت الانتهاء'
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ملاحظات الجلسة'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'جلسة التقييم'
        verbose_name_plural = 'جلسات التقييم'
        ordering = ['-session_date', '-created_at']
        unique_together = ['plan', 'session_date']

    def __str__(self):
        return f'تقييم {self.plan.title} - {self.session_date}'

    def clean(self):
        """Validate that only one session can be active at a time"""
        if self.status == 'active':
            # Check if there are other active sessions
            active_sessions = EvaluationSession.objects.filter(status='active')
            if self.pk:
                active_sessions = active_sessions.exclude(pk=self.pk)

            if active_sessions.exists():
                raise ValidationError(
                    'يمكن أن يكون هناك جلسة تقييم نشطة واحدة فقط في نفس الوقت. '
                    'يرجى إيقاف الجلسات النشطة الأخرى أولاً.'
                )

    @property
    def total_candidates(self):
        """Total number of candidates in this plan"""
        return self.plan.candidates.count()

    @property
    def evaluated_candidates_count(self):
        """Number of candidates that have been evaluated"""
        return self.candidate_evaluations.filter(is_completed=True).count()

    @property
    def remaining_candidates_count(self):
        """Number of candidates remaining to be evaluated"""
        return self.total_candidates - self.evaluated_candidates_count

    @property
    def progress_percentage(self):
        """Progress percentage of the evaluation session"""
        if self.total_candidates == 0:
            return 0
        return round((self.evaluated_candidates_count / self.total_candidates) * 100, 1)

    def get_next_candidate(self):
        """Get the next candidate to be evaluated"""
        evaluated_candidates = self.candidate_evaluations.filter(
            is_completed=True
        ).values_list('candidate_id', flat=True)

        return self.plan.candidates.exclude(
            id__in=evaluated_candidates
        ).first()

    def start_session(self):
        """Start the evaluation session"""
        # Check if there are any other active sessions and deactivate them
        active_sessions = EvaluationSession.objects.filter(status='active').exclude(id=self.id)
        if active_sessions.exists():
            # Pause all other active sessions
            active_sessions.update(status='paused')

        self.status = 'active'
        self.start_time = timezone.now()
        if not self.current_candidate:
            self.current_candidate = self.get_next_candidate()
        self.save()

    def complete_session(self):
        """Complete the evaluation session"""
        self.status = 'completed'
        self.end_time = timezone.now()
        self.current_candidate = None
        self.save()

    def pause_session(self):
        """Pause the evaluation session"""
        self.status = 'paused'
        self.save()

    def resume_session(self):
        """Resume the evaluation session"""
        # Check if there are any other active sessions and deactivate them
        active_sessions = EvaluationSession.objects.filter(status='active').exclude(id=self.id)
        if active_sessions.exists():
            # Pause all other active sessions
            active_sessions.update(status='paused')

        self.status = 'active'
        self.save()


class EvaluationQuestion(models.Model):
    """Questions used in candidate evaluation"""

    QUESTION_TYPES = [
        ('mcq', 'اختيار من متعدد'),
        ('true_false', 'صح أم خطأ'),
        ('qa', 'سؤال وجواب'),
    ]

    question_text = models.TextField(
        verbose_name='نص السؤال',
        default='سؤال جديد'
    )

    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='mcq',
        verbose_name='نوع السؤال'
    )

    # For Q&A questions
    answer = models.TextField(
        blank=True,
        null=True,
        verbose_name='الإجابة',
        help_text='الإجابة النموذجية للسؤال'
    )

    # For MCQ questions
    option_a = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='الخيار أ'
    )

    option_b = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='الخيار ب'
    )

    option_c = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='الخيار ج'
    )

    option_d = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='الخيار د'
    )

    # Correct answer for MCQ and True/False
    correct_answer = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='الإجابة الصحيحة',
        help_text='للاختيار من متعدد: A, B, C, D | للصح والخطأ: True, False'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'سؤال التقييم'
        verbose_name_plural = 'أسئلة التقييم'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.question_text[:50]}... ({self.get_question_type_display()})'

    @classmethod
    def get_random_question_by_type(cls, question_type):
        """Get a random question by type"""
        import random
        questions = cls.objects.filter(
            question_type=question_type,
            is_active=True
        )
        if questions.exists():
            return random.choice(questions)
        return None

    @classmethod
    def get_random_mcq(cls):
        """Get a random MCQ question"""
        return cls.get_random_question_by_type('mcq')

    @classmethod
    def get_random_true_false(cls):
        """Get a random True/False question"""
        return cls.get_random_question_by_type('true_false')

    @classmethod
    def get_random_qa(cls):
        """Get a random Q&A question"""
        return cls.get_random_question_by_type('qa')

    def get_options_list(self):
        """Get MCQ options as list"""
        if self.question_type == 'mcq':
            options = []
            if self.option_a: options.append(('A', self.option_a))
            if self.option_b: options.append(('B', self.option_b))
            if self.option_c: options.append(('C', self.option_c))
            if self.option_d: options.append(('D', self.option_d))
            return options
        return []

    def is_correct_answer(self, user_answer):
        """Check if user answer is correct"""
        if self.correct_answer:
            return str(user_answer).upper() == str(self.correct_answer).upper()
        return False


class CandidateEvaluation(models.Model):
    """Individual candidate evaluation within a session"""

    session = models.ForeignKey(
        EvaluationSession,
        on_delete=models.CASCADE,
        related_name='candidate_evaluations',
        verbose_name='جلسة التقييم'
    )

    candidate = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='المرشح'
    )

    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conducted_evaluations',
        verbose_name='المقيم'
    )

    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='وقت البداية'
    )

    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='وقت الانتهاء'
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name='مكتمل'
    )

    total_score = models.FloatField(
        default=0.0,
        verbose_name='الدرجة الإجمالية'
    )

    max_possible_score = models.FloatField(
        default=0.0,
        verbose_name='أقصى درجة ممكنة'
    )

    general_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ملاحظات عامة'
    )

    recommendation = models.CharField(
        max_length=50,
        choices=[
            ('highly_recommended', 'مُوصى به بقوة'),
            ('recommended', 'مُوصى به'),
            ('neutral', 'متوسط'),
            ('not_recommended', 'غير مُوصى به'),
            ('rejected', 'مرفوض'),
        ],
        blank=True,
        null=True,
        verbose_name='التوصية'
    )

    class Meta:
        verbose_name = 'تقييم المرشح'
        verbose_name_plural = 'تقييمات المرشحين'
        unique_together = ['session', 'candidate', 'evaluator']
        ordering = ['-start_time']

    def __str__(self):
        return f'تقييم {self.candidate.student_name} - {self.session.session_date}'

    @property
    def duration_minutes(self):
        """Duration of evaluation in minutes"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 60
        return None

    @property
    def score_percentage(self):
        """Score as percentage"""
        if self.max_possible_score > 0:
            return round((self.total_score / self.max_possible_score) * 100, 1)
        return 0

    def calculate_total_score(self):
        """Calculate total score from all answers"""
        answers = self.answers.all()
        total = 0
        max_total = 0

        for answer in answers:
            if answer.question.question_type in ['numeric', 'rating']:
                weighted_score = answer.score * answer.question.weight
                max_weighted_score = answer.question.max_score * answer.question.weight
                total += weighted_score
                max_total += max_weighted_score

        self.total_score = total
        self.max_possible_score = max_total
        self.save()

        return total

    def complete_evaluation(self):
        """Mark evaluation as complete"""
        self.end_time = timezone.now()
        self.is_completed = True
        self.calculate_total_score()
        self.save()


class EvaluationAnswer(models.Model):
    """Individual answers to evaluation questions"""

    evaluation = models.ForeignKey(
        CandidateEvaluation,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='التقييم'
    )

    question = models.ForeignKey(
        EvaluationQuestion,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='السؤال'
    )

    score = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='الدرجة'
    )

    text_answer = models.TextField(
        blank=True,
        null=True,
        verbose_name='الإجابة النصية'
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ملاحظات'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'إجابة التقييم'
        verbose_name_plural = 'إجابات التقييم'
        unique_together = ['evaluation', 'question']

    def __str__(self):
        return f'{self.question.title}: {self.score}/{self.question.max_score}'

    def clean(self):
        """Validate score doesn't exceed question's max score"""
        if self.score > self.question.max_score:
            raise ValidationError(f'الدرجة لا يمكن أن تتجاوز {self.question.max_score}')


class EvaluationTemplate(models.Model):
    """Template for evaluation questions to be reused across sessions"""

    name = models.CharField(
        max_length=100,
        verbose_name='اسم القالب'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='وصف القالب'
    )

    questions = models.ManyToManyField(
        EvaluationQuestion,
        related_name='templates',
        verbose_name='الأسئلة'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'قالب التقييم'
        verbose_name_plural = 'قوالب التقييم'
        ordering = ['name']

    def __str__(self):
        return self.name


class EvaluationTopic(models.Model):
    """Generic evaluation topic like Personal Appearance, Communication Skills, etc."""

    name = models.CharField(
        max_length=100,
        verbose_name='اسم المحور'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='وصف المحور'
    )

    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0)],
        verbose_name='الوزن النسبي',
        help_text='الوزن النسبي للمحور في التقييم الإجمالي'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )

    order = models.PositiveIntegerField(
        default=1,
        verbose_name='الترتيب'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'محور التقييم'
        verbose_name_plural = 'محاور التقييم'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class EvaluationCriteria(models.Model):
    """Scoring criteria for evaluation topics (e.g., ضعيف، جيد، جيد جداً، ممتاز)"""

    topic = models.ForeignKey(
        EvaluationTopic,
        on_delete=models.CASCADE,
        related_name='criteria',
        verbose_name='المحور'
    )

    name = models.CharField(
        max_length=50,
        verbose_name='اسم المعيار'
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='وصف المعيار'
    )

    # score_percentage will be calculated automatically based on order
    # No need for a database field

    order = models.PositiveIntegerField(
        default=1,
        verbose_name='الترتيب'
    )

    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='لون المعيار',
        help_text='لون المعيار في الواجهة (hex color)'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'معيار التقييم'
        verbose_name_plural = 'معايير التقييم'
        ordering = ['topic', 'order']
        unique_together = ['topic', 'name']

    def __str__(self):
        return f'{self.topic.name} - {self.name}'

    @property
    def score_percentage(self):
        """
        Calculate score percentage automatically based on criteria order.
        Formula: (order / total_criteria_in_topic) * 100

        Examples:
        - 2 criteria: weak=50%, excellent=100%
        - 4 criteria: weak=25%, good=50%, very good=75%, excellent=100%
        """
        total_criteria = EvaluationCriteria.objects.filter(topic=self.topic).count()
        if total_criteria == 0:
            return 0
        return (self.order / total_criteria) * 100

    def clean(self):
        """Validation for evaluation criteria"""
        # No need to validate percentages as they are calculated automatically
        # Just ensure order is positive
        if self.order <= 0:
            raise ValidationError('ترتيب المعيار يجب أن يكون أكبر من صفر')


class CandidateTopicEvaluation(models.Model):
    """Individual candidate evaluation for specific topics"""

    session = models.ForeignKey(
        EvaluationSession,
        on_delete=models.CASCADE,
        related_name='topic_evaluations',
        verbose_name='جلسة التقييم'
    )

    candidate = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='topic_evaluations',
        verbose_name='المرشح'
    )

    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='topic_evaluations',
        verbose_name='المقيم'
    )

    topic = models.ForeignKey(
        EvaluationTopic,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='المحور'
    )

    criteria = models.ForeignKey(
        EvaluationCriteria,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='المعيار المحدد'
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ملاحظات'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تقييم محور المرشح'
        verbose_name_plural = 'تقييمات محاور المرشحين'
        unique_together = ['session', 'candidate', 'evaluator', 'topic']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.candidate.student_name} - {self.topic.name}: {self.criteria.name}'

    @property
    def score_percentage(self):
        """Get the percentage score for this evaluation"""
        return self.criteria.score_percentage

    def clean(self):
        """Validate that criteria belongs to the topic"""
        if self.criteria and self.topic and self.criteria.topic != self.topic:
            raise ValidationError('المعيار المحدد لا ينتمي للمحور المحدد')


class EvaluationReport(models.Model):
    """Complete evaluation report snapshot for a candidate by an evaluator"""

    session = models.ForeignKey(
        EvaluationSession,
        on_delete=models.CASCADE,
        related_name='evaluation_reports',
        verbose_name='جلسة التقييم'
    )

    candidate = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='evaluation_reports',
        verbose_name='المرشح'
    )

    evaluator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='evaluation_reports',
        verbose_name='المقيم'
    )

    # Summary scores
    total_weighted_score = models.FloatField(
        verbose_name='المجموع المرجح'
    )

    total_possible_score = models.FloatField(
        verbose_name='المجموع الأقصى الممكن'
    )

    overall_percentage = models.FloatField(
        verbose_name='النسبة المئوية الإجمالية'
    )

    # Detailed evaluation data (JSON field for flexibility)
    evaluation_data = models.JSONField(
        verbose_name='بيانات التقييم التفصيلية',
        help_text='يحتوي على التقييمات التفصيلية لكل محور'
    )

    # General notes
    general_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ملاحظات عامة'
    )

    # Status
    is_finalized = models.BooleanField(
        default=True,
        verbose_name='نهائي'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تقرير تقييم المرشح'
        verbose_name_plural = 'تقارير تقييم المرشحين'
        unique_together = ['session', 'candidate', 'evaluator']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.candidate.student_name} - {self.evaluator.get_full_name() or self.evaluator.username} ({self.overall_percentage:.1f}%)'

    @property
    def grade_text(self):
        """Get grade text based on percentage"""
        if self.overall_percentage >= 85:
            return 'ممتاز'
        elif self.overall_percentage >= 75:
            return 'جيد جداً'
        elif self.overall_percentage >= 60:
            return 'جيد'
        else:
            return 'ضعيف'

    @property
    def grade_color(self):
        """Get grade color based on percentage"""
        if self.overall_percentage >= 85:
            return 'success'
        elif self.overall_percentage >= 75:
            return 'info'
        elif self.overall_percentage >= 60:
            return 'warning'
        else:
            return 'danger'
