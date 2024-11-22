from django import template
import re

register = template.Library()


# Converts string "69 420" to float 69420
@register.filter
def to_number(value):
    try:
        return float(value.replace(" ", ""))
    except (ValueError, AttributeError):
        return 0


@register.filter
def to_lowercase(value):
    try:
        return str(value).lower()
    except (ValueError, AttributeError):
        return value


# Formats numbers with spaces as thousand separators
@register.filter
def spaced_number(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)


# Formats numbers with spaces as thousand separators
@register.filter
def dec_to_float(value):
    try:
        value = str(value)
        value = value.replace(",", ".")
        return value
    except (ValueError, TypeError):
        return str(value)


@register.filter
def dec_to_int(value):
    try:
        value = str(value)
        if "," in value:
            value = value.split(",")[0]

        return int(value)
    except (ValueError, TypeError):
        return value


@register.filter
def extract_number(value):
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group())
    return None


@register.filter
def sort_categories(categories):
    sorted_categories = []
    for category in categories:
        sorted_categories.append(category.name)

    sorted_categories.sort()
    return sorted_categories


@register.filter
def zip_lists(list1, list2):
    return zip(list1, list2)
