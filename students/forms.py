from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import Person, Qualification, Experience, Plan


class PersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order plans by latest created and only show active plans
        self.fields['plan'].queryset = Plan.objects.filter(is_active=True).order_by('-created_at')
        self.fields['plan'].empty_label = "اختر خطة التوظيف..."

    class Meta:
        model = Person
        fields = [
            'student_name', 'personal_image', 'birth_date', 'gender',
            'primary_qualification', 'university', 'general_degree', 'graduation_year',
            'marital_status', 'number_of_children', 'address', 'phone_number', 'email', 'plan'
        ]
        widgets = {
            'student_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'primary_qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor of Engineering'
            }),
            'university': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'University/Institution name'
            }),
            'general_degree': forms.Select(attrs={
                'class': 'form-control'
            }),
            'graduation_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1950',
                'max': str(timezone.now().year + 10)
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'number_of_children': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '20'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'candidate@example.com'
            }),
            'personal_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'plan': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            })
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 16:
                raise ValidationError("Candidate must be at least 16 years old.")
            if age > 100:
                raise ValidationError("Please enter a valid birth date.")
        return birth_date

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (excluding current instance)
            existing = Person.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("A candidate with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            import re

            # Convert Arabic numerals to English numerals
            arabic_to_english = {
                '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
            }

            # Replace Arabic numbers with English numbers
            normalized_phone = phone
            for arabic_digit, english_digit in arabic_to_english.items():
                normalized_phone = normalized_phone.replace(arabic_digit, english_digit)

            # Remove any spaces, dashes, or parentheses
            clean_phone = re.sub(r'[\s\-\(\)]', '', normalized_phone)

            # Egyptian phone number validation
            # Format: 01XXXXXXXXX (11 digits starting with 01)
            # Valid prefixes: 010, 011, 012, 015 (major carriers)
            egyptian_pattern = re.compile(r'^01[0125]\d{8}$')

            if not egyptian_pattern.match(clean_phone):
                raise ValidationError("يرجى إدخال رقم هاتف مصري صحيح (مثال: 01012345678)")

            # Store the normalized phone number
            return clean_phone
        return phone


class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = ['person', 'degree_name', 'degree_date']
        widgets = {
            'person': forms.Select(attrs={
                'class': 'form-control'
            }),
            'degree_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Master of Computer Science'
            }),
            'degree_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def clean_degree_date(self):
        degree_date = self.cleaned_data.get('degree_date')
        if degree_date and degree_date > date.today():
            raise ValidationError("Degree date cannot be in the future.")
        return degree_date


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['person', 'job_title', 'company_name', 'start_date', 'end_date']
        widgets = {
            'person': forms.Select(attrs={
                'class': 'form-control'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Software Developer'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise ValidationError("End date must be after start date.")

        if start_date and start_date > date.today():
            raise ValidationError("Start date cannot be in the future.")

        if end_date and end_date > date.today():
            raise ValidationError("End date cannot be in the future.")

        return cleaned_data


class CandidateSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or qualification...'
        })
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'All Genders')] + Person.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    general_degree = forms.ChoiceField(
        required=False,
        choices=[('', 'All Grades')] + Person.GENERAL_DEGREE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    marital_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Person.MARITAL_STATUS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    university = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'University name...'
        })
    )
    min_age = forms.IntegerField(
        required=False,
        min_value=16,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min age'
        })
    )
    max_age = forms.IntegerField(
        required=False,
        min_value=16,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max age'
        })
    )
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.all(),
        required=False,
        empty_label="All Plans",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        min_age = cleaned_data.get('min_age')
        max_age = cleaned_data.get('max_age')

        if min_age and max_age and min_age > max_age:
            raise ValidationError("Minimum age cannot be greater than maximum age.")

        return cleaned_data


class BulkActionForm(forms.Form):
    ACTION_CHOICES = [
        ('', 'Select action...'),
        ('export_csv', 'Export to CSV'),
        ('export_excel', 'Export to Excel'),
        ('delete', 'Delete selected'),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    selected_candidates = forms.CharField(
        widget=forms.HiddenInput()
    )


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['title', 'department', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: اختبارات لصالح فرع النظم ٢٠٢٥'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: فرع النظم'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'ملاحظات أو تفاصيل إضافية حول الخطة...'
            })
        }




class PlanSelectionForm(forms.Form):
    """Form for selecting a plan for evaluation"""
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.all().order_by('-created_at'),
        empty_label="Select a recruitment plan...",
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg'
        }),
        help_text="Choose the recruitment plan to start evaluation"
    )


class PreviousTestForm(forms.Form):
    """Dynamic form for adding previous test scores during candidate registration"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add fields based on active PreviousTestTemplate objects
        from examinations.models import PreviousTestTemplate

        templates = PreviousTestTemplate.objects.filter(is_active=True).order_by('order', 'name')

        for template in templates:
            field_name = f'test_{template.id}'
            self.fields[field_name] = forms.IntegerField(
                required=False,
                min_value=0,
                max_value=template.max_score,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': f'درجة {template.name_arabic}',
                    'min': '0',
                    'max': str(template.max_score)
                }),
                label=f'درجة {template.name_arabic}',
                help_text=f'الدرجة من {template.max_score}'
            )

    def get_test_data(self):
        """Return test data in a format suitable for saving"""
        from examinations.models import PreviousTestTemplate

        tests = []
        templates = PreviousTestTemplate.objects.filter(is_active=True)

        for template in templates:
            field_name = f'test_{template.id}'
            score = self.cleaned_data.get(field_name)
            if score is not None:
                tests.append({
                    'template': template,
                    'name': template.name,
                    'name_arabic': template.name_arabic,
                    'score': score,
                    'max_score': template.max_score
                })

        return tests

    def get_template_fields(self):
        """Return template objects with their corresponding field names for template rendering"""
        from examinations.models import PreviousTestTemplate

        templates = PreviousTestTemplate.objects.filter(is_active=True).order_by('order', 'name')
        template_fields = []

        for template in templates:
            field_name = f'test_{template.id}'
            template_fields.append({
                'template': template,
                'field': self[field_name],
                'field_name': field_name
            })

        return template_fields