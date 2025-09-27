from django import forms
from django.utils import timezone
from students.models import Plan
from .models import EvaluationSession, CandidateEvaluation, EvaluationAnswer, EvaluationQuestion


class EvaluationSessionForm(forms.ModelForm):
    class Meta:
        model = EvaluationSession
        fields = ['plan', 'session_date', 'notes']
        widgets = {
            'plan': forms.Select(attrs={'class': 'form-control'}),
            'session_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'value': timezone.now().date()
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'ملاحظات إضافية عن الجلسة (اختيارية)'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show plans that have candidates
        self.fields['plan'].queryset = Plan.objects.filter(
            candidates__isnull=False
        ).distinct().order_by('-created_at')

        # Set labels in Arabic
        self.fields['plan'].label = 'خطة التوظيف'
        self.fields['session_date'].label = 'تاريخ الجلسة'
        self.fields['notes'].label = 'ملاحظات'

        # Make notes optional
        self.fields['notes'].required = False

    def clean_session_date(self):
        session_date = self.cleaned_data['session_date']

        # Don't allow dates in the past (unless updating existing session)
        if not self.instance.pk and session_date < timezone.now().date():
            raise forms.ValidationError('لا يمكن إنشاء جلسة في تاريخ سابق.')

        return session_date

    def clean(self):
        cleaned_data = super().clean()
        plan = cleaned_data.get('plan')
        session_date = cleaned_data.get('session_date')

        if plan and session_date:
            # Check if there's already a session for this plan on this date
            existing_session = EvaluationSession.objects.filter(
                plan=plan,
                session_date=session_date
            )

            # If updating, exclude current instance
            if self.instance.pk:
                existing_session = existing_session.exclude(pk=self.instance.pk)

            if existing_session.exists():
                raise forms.ValidationError(
                    f'توجد جلسة تقييم أخرى لخطة "{plan.title}" في نفس التاريخ.'
                )

        return cleaned_data


class CandidateEvaluationForm(forms.ModelForm):
    class Meta:
        model = CandidateEvaluation
        fields = ['general_notes', 'recommendation']
        widgets = {
            'general_notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'ملاحظات عامة حول أداء المرشح'
                }
            ),
            'recommendation': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set labels in Arabic
        self.fields['general_notes'].label = 'الملاحظات العامة'
        self.fields['recommendation'].label = 'التوصية النهائية'

        # Make fields optional initially
        self.fields['general_notes'].required = False
        self.fields['recommendation'].required = False


class EvaluationAnswerForm(forms.ModelForm):
    class Meta:
        model = EvaluationAnswer
        fields = ['score', 'text_answer', 'notes']
        widgets = {
            'score': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '0.1'
                }
            ),
            'text_answer': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'ملاحظات إضافية'
                }
            ),
        }

    def __init__(self, question=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if question:
            self.question = question

            # Set max value for score field
            self.fields['score'].widget.attrs['max'] = str(question.max_score)

            # Set labels
            self.fields['score'].label = f'النقاط (من {question.max_score})'
            self.fields['text_answer'].label = 'الإجابة النصية'
            self.fields['notes'].label = 'ملاحظات'

            # Configure fields based on question type
            if question.question_type in ['numeric', 'rating']:
                self.fields['score'].required = question.is_required
                self.fields['text_answer'].required = False
            elif question.question_type == 'text':
                self.fields['score'].required = False
                self.fields['text_answer'].required = question.is_required
                # Hide score field for text questions
                self.fields['score'].widget = forms.HiddenInput()
            else:  # choice type
                self.fields['score'].required = question.is_required
                self.fields['text_answer'].required = False

            # Notes are always optional
            self.fields['notes'].required = False

    def clean_score(self):
        score = self.cleaned_data.get('score')

        if score is not None and hasattr(self, 'question'):
            if score < 0:
                raise forms.ValidationError('النقاط لا يمكن أن تكون أقل من صفر.')
            if score > self.question.max_score:
                raise forms.ValidationError(
                    f'النقاط لا يمكن أن تتجاوز {self.question.max_score}.'
                )

        return score


class QuestionAnswerFormSet(forms.BaseFormSet):
    """Custom formset for handling multiple question answers"""

    def __init__(self, questions=None, evaluation=None, *args, **kwargs):
        self.questions = questions or []
        self.evaluation = evaluation
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        """Return additional keyword arguments for each form."""
        kwargs = super().get_form_kwargs(index)
        if index < len(self.questions):
            kwargs['question'] = self.questions[index]
        return kwargs

    def save(self, commit=True):
        """Save all forms in the formset"""
        instances = []

        for form in self.forms:
            if form.is_valid() and form.cleaned_data:
                instance = form.save(commit=False)

                # Set the evaluation and question
                if hasattr(form, 'question') and self.evaluation:
                    instance.evaluation = self.evaluation
                    instance.question = form.question

                    # For text questions, set score to 0
                    if form.question.question_type == 'text':
                        instance.score = 0

                if commit:
                    instance.save()

                instances.append(instance)

        return instances


class EvaluationQuestionForm(forms.ModelForm):
    """Form for creating/editing evaluation questions"""

    class Meta:
        model = EvaluationQuestion
        fields = [
            'question_text', 'question_type', 'answer',
            'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'is_active'
        ]
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set Arabic labels
        self.fields['question_text'].label = 'نص السؤال'
        self.fields['question_type'].label = 'نوع السؤال'
        self.fields['answer'].label = 'الإجابة'
        self.fields['option_a'].label = 'الخيار أ'
        self.fields['option_b'].label = 'الخيار ب'
        self.fields['option_c'].label = 'الخيار ج'
        self.fields['option_d'].label = 'الخيار د'
        self.fields['correct_answer'].label = 'الإجابة الصحيحة'
        self.fields['is_active'].label = 'نشط'

        # Make all fields optional initially
        self.fields['answer'].required = False
        self.fields['option_a'].required = False
        self.fields['option_b'].required = False
        self.fields['option_c'].required = False
        self.fields['option_d'].required = False
        self.fields['correct_answer'].required = False

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        answer = cleaned_data.get('answer')
        option_a = cleaned_data.get('option_a')
        option_b = cleaned_data.get('option_b')
        correct_answer = cleaned_data.get('correct_answer')

        # Validate based on question type
        if question_type == 'qa':
            if not answer:
                raise forms.ValidationError({
                    'answer': 'الإجابة مطلوبة لأسئلة السؤال والجواب.'
                })

        elif question_type == 'mcq':
            if not option_a or not option_b:
                raise forms.ValidationError('الخيارات أ و ب مطلوبة على الأقل للاختيار من متعدد.')

            if not correct_answer:
                raise forms.ValidationError({
                    'correct_answer': 'الإجابة الصحيحة مطلوبة (A, B, C, أو D).'
                })

            if correct_answer.upper() not in ['A', 'B', 'C', 'D']:
                raise forms.ValidationError({
                    'correct_answer': 'الإجابة الصحيحة يجب أن تكون A أو B أو C أو D.'
                })

        elif question_type == 'true_false':
            if not correct_answer:
                raise forms.ValidationError({
                    'correct_answer': 'الإجابة الصحيحة مطلوبة (True أو False).'
                })

            if correct_answer.upper() not in ['TRUE', 'FALSE']:
                raise forms.ValidationError({
                    'correct_answer': 'الإجابة الصحيحة يجب أن تكون True أو False.'
                })

        return cleaned_data


# Create formset factory
EvaluationAnswerFormSet = forms.formset_factory(
    EvaluationAnswerForm,
    formset=QuestionAnswerFormSet,
    extra=0,
    can_delete=False
)