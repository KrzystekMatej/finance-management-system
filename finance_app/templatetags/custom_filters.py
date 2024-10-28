from django import template

register = template.Library()

# Converts string "69 420" to float 69420 @register.filter
def to_number(value):
    try:
        return float(value.replace(" ", ""))
    except (ValueError, AttributeError):
        return 0

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
