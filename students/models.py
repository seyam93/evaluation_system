from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date


class Plan(models.Model):
    """
    Recruitment Plan - Simple plan with only essential fields
    Each plan can have multiple candidates applying for it
    """
    # Simple fields only
    title = models.CharField(max_length=200, verbose_name="اسم الخطة")
    department = models.CharField(max_length=100, verbose_name="لصالح")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")

    # Metadata (keep for tracking)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "خطة التوظيف"
        verbose_name_plural = "خطط التوظيف"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.department}"

    @property
    def candidates_count(self):
        """Return number of candidates applied to this plan"""
        return self.candidates.count()


class Person(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    MARITAL_STATUS = [
        ('single', 'single'),
        ('married', 'married'),
    ]
    GENERAL_DEGREE = [
        ('Excellent', 'Excellent'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Sufficient', 'Sufficient'),
    ]

    student_name = models.CharField(max_length=255, verbose_name="Student Name", blank=True, null=True)
    personal_image = models.ImageField(upload_to='candidates/photos/', blank=True, null=True, verbose_name="Personal Photo", default='images/profile.png')
    birth_date = models.DateField(verbose_name="Date of Birth", help_text="Student's date of birth", blank=True, null=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, verbose_name="Gender", blank=True, null=True)
    primary_qualification = models.CharField(max_length=100, blank=True, null=True, verbose_name="Primary Qualification")
    university = models.CharField(max_length=200, blank=True, null=True, verbose_name="University/Institution")
    general_degree = models.CharField(max_length=15, choices=GENERAL_DEGREE, verbose_name="Overall Grade", blank=True, null=True)
    graduation_year = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1950),
            MaxValueValidator(timezone.now().year + 10)
        ],
        verbose_name="Graduation Year"
    )
    marital_status = models.CharField(max_length=8, choices=MARITAL_STATUS, verbose_name="Marital Status", blank=True, null=True)
    number_of_children = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name="Number of Children",
        default=0
    )
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    email = models.EmailField(blank=True, null=True, verbose_name="Email Address")

    # Plan relationship - link candidate to a recruitment plan
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name="candidates",
        verbose_name="خطة التوظيف",
        help_text="الخطة التي تقدم لها المرشح"
    )

    # Application status for this specific plan
    APPLICATION_STATUS_CHOICES = [
        ('applied', 'تم التقديم'),
        ('screening', 'فرز أولي'),
        ('interview_scheduled', 'مقابلة مجدولة'),
        ('interviewed', 'تمت المقابلة'),
        ('accepted', 'مقبول'),
        ('rejected', 'مرفوض'),
        ('on_hold', 'معلق'),
    ]

    application_status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='applied',
        verbose_name="حالة التقديم"
    )

    application_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التقديم")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.student_name or "Unnamed Student"

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def get_profile_image_url(self):
        """Return the profile image URL or default image if none exists"""
        if self.personal_image and hasattr(self.personal_image, 'url'):
            return self.personal_image.url
        else:
            from django.templatetags.static import static
            return static('images/profile.png')

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['student_name']


class Qualification(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="qualifications")
    degree_name = models.CharField(max_length=255)
    degree_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.degree_name} - {self.person.student_name}"

    class Meta:
        verbose_name = "Qualification"
        verbose_name_plural = "Qualifications"
        ordering = ['-degree_date']


class Experience(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="experiences")
    job_title = models.CharField(max_length=255)  
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)   

    def __str__(self):
        return f"{self.job_title} at {self.company_name or 'Unknown Company'} ({self.person.student_name})"

    @property
    def duration_years(self):
        if self.start_date:
            end = self.end_date or date.today()
            return (end - self.start_date).days / 365.25
        return None

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"
        ordering = ['-start_date']

