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

@register.filter
def arabic_numbers(value):
    """Convert English numbers to Arabic numbers"""
    if value is None:
        return value

    # Convert value to string
    value_str = str(value)

    # Mapping from English to Arabic numerals
    english_to_arabic = {
        '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
    }

    # Replace each English digit with Arabic digit
    for english, arabic in english_to_arabic.items():
        value_str = value_str.replace(english, arabic)

    return value_str