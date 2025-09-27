from django.db import models
from students.models import Person
from django.core.validators import MinValueValidator, MaxValueValidator


class TestCategory(models.Model):
    """Test categories like English, IT, Psychology, etc."""
    EXAMINATION_TYPES = [
        ('previous_test', 'Previous Test'),
        ('interview_evaluation', 'Interview Evaluation'),
    ]

    name = models.CharField(max_length=100, verbose_name="Test Category")
    examination_type = models.CharField(
        max_length=20,
        choices=EXAMINATION_TYPES,
        default='previous_test',
        verbose_name="Examination Type"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    max_score = models.IntegerField(default=100, verbose_name="Maximum Score")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_examination_type_display()})"

    class Meta:
        verbose_name = "Test Category"
        verbose_name_plural = "Test Categories"
        ordering = ['examination_type', 'name']
        unique_together = ['name', 'examination_type']


class CandidateTest(models.Model):
    """Individual test results for candidates - supports both previous tests and interview evaluations"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='test_results')
    test_category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Score"
    )
    max_possible_score = models.IntegerField(default=100, verbose_name="Max Possible Score")
    test_date = models.DateField(null=True, blank=True, verbose_name="Test Date")
    notes = models.TextField(blank=True, null=True, verbose_name="Additional Notes")

    # For previous tests - can be entered during registration
    is_previous_test = models.BooleanField(default=False, verbose_name="Is Previous Test")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        test_type = "Previous Test" if self.is_previous_test else "Interview Test"
        return f"{self.person.student_name} - {self.test_category.name} ({test_type}): {self.score}/{self.max_possible_score}"

    @property
    def percentage_score(self):
        if self.max_possible_score > 0:
            return round((self.score / self.max_possible_score) * 100, 2)
        return 0

    @property
    def grade(self):
        percentage = self.percentage_score
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    @property
    def grade_arabic(self):
        """Arabic grade representation"""
        grade = self.grade
        grade_map = {
            'A': 'ممتاز',
            'B': 'جيد جداً',
            'C': 'جيد',
            'D': 'مقبول',
            'F': 'راسب'
        }
        return grade_map.get(grade, 'غير محدد')

    class Meta:
        verbose_name = "Candidate Test Result"
        verbose_name_plural = "Candidate Test Results"
        unique_together = ['person', 'test_category']
        ordering = ['-is_previous_test', '-test_date', 'test_category__name']


class CandidateTestSummary(models.Model):
    """Summary of all tests for a candidate"""
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='test_summary')
    total_tests_taken = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    highest_score = models.IntegerField(default=0)
    lowest_score = models.IntegerField(default=0)
    last_test_date = models.DateField(null=True, blank=True)
    overall_grade = models.CharField(max_length=2, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Test Summary for {self.person.student_name}"

    def update_summary(self):
        """Update summary based on current test results"""
        tests = self.person.test_results.all()
        if tests.exists():
            scores = [test.percentage_score for test in tests]
            self.total_tests_taken = tests.count()
            self.average_score = sum(scores) / len(scores)
            self.highest_score = max(scores)
            self.lowest_score = min(scores)
            self.last_test_date = tests.latest('test_date').test_date

            # Calculate overall grade based on average
            if self.average_score >= 90:
                self.overall_grade = 'A'
            elif self.average_score >= 80:
                self.overall_grade = 'B'
            elif self.average_score >= 70:
                self.overall_grade = 'C'
            elif self.average_score >= 60:
                self.overall_grade = 'D'
            else:
                self.overall_grade = 'F'
        else:
            self.total_tests_taken = 0
            self.average_score = 0.0
            self.highest_score = 0
            self.lowest_score = 0
            self.last_test_date = None
            self.overall_grade = None

        self.save()

    class Meta:
        verbose_name = "Candidate Test Summary"
        verbose_name_plural = "Candidate Test Summaries"


class PreviousTestTemplate(models.Model):
    """Template for common previous tests that candidates typically take"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Test Name")
    name_arabic = models.CharField(max_length=100, verbose_name="Test Name (Arabic)")
    max_score = models.IntegerField(default=100, verbose_name="Maximum Score")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    order = models.IntegerField(default=0, verbose_name="Display Order")

    def __str__(self):
        return f"{self.name_arabic} ({self.name})"

    class Meta:
        verbose_name = "Previous Test Template"
        verbose_name_plural = "Previous Test Templates"
        ordering = ['order', 'name']


# Keep the old model for backward compatibility but mark as deprecated
class Previoustests(models.Model):
    """DEPRECATED: Use CandidateTest instead"""
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name='previoustests_old')
    english_degree = models.IntegerField(blank=True, null=True)
    it_degree = models.IntegerField(blank=True, null=True)
    information_degree = models.IntegerField(blank=True, null=True)
    nafsy_degree = models.IntegerField(blank=True, null=True)
    security_degree = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"[DEPRECATED] Tests for {self.person.student_name}"

    class Meta:
        verbose_name = "[DEPRECATED] Previous Tests"
        verbose_name_plural = "[DEPRECATED] Previous Tests"


# Helper methods for easy access to previous tests
def get_previous_tests_for_person(person):
    """Get all previous tests for a person"""
    return CandidateTest.objects.filter(person=person, is_previous_test=True)


def get_interview_tests_for_person(person):
    """Get all interview tests for a person"""
    return CandidateTest.objects.filter(person=person, is_previous_test=False)
