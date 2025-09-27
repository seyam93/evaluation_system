from django import template
from examinations.models import get_previous_tests_for_person, get_interview_tests_for_person

register = template.Library()


@register.simple_tag
def get_previous_tests(person):
    """Get all previous tests for a person"""
    return get_previous_tests_for_person(person)


@register.simple_tag
def get_interview_tests(person):
    """Get all interview tests for a person"""
    return get_interview_tests_for_person(person)


@register.filter
def test_score_percentage(test):
    """Get percentage score for a test"""
    if hasattr(test, 'percentage_score'):
        return test.percentage_score
    return 0


@register.filter
def test_grade_class(grade):
    """Get CSS class for test grade"""
    grade_classes = {
        'A': 'bg-success',
        'B': 'bg-info',
        'C': 'bg-warning',
        'D': 'bg-secondary',
        'F': 'bg-danger'
    }
    return grade_classes.get(grade, 'bg-secondary')