from django import template

register = template.Library()


# Converts string "69 420" to float 69420
@register.filter
def to_number(value):
    try:
        return float(value.replace(" ", ""))
    except (ValueError, AttributeError):
        return 0


@register.filter
def spaced_number(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)
