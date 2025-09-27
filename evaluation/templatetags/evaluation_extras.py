from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup values in dictionary by key"""
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def get_score(existing_answers, question_id):
    """Get score for a specific question from existing answers"""
    answer = existing_answers.get(question_id)
    return answer.score if answer else 0

@register.filter
def get_notes(existing_answers, question_id):
    """Get notes for a specific question from existing answers"""
    answer = existing_answers.get(question_id)
    return answer.notes if answer else ''