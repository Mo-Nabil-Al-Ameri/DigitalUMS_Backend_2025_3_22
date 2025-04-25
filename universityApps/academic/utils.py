import string

def generate_group_name_en(index):
    letters = string.ascii_uppercase  # A-Z
    base = len(letters)

    if index < base:
        return f"Group {letters[index]}"
    else:
        # دعم للأسماء مثل: Group AA, AB, ..., ZZ
        first = letters[(index // base) - 1]
        second = letters[index % base]
        return f"Group {first}{second}"
