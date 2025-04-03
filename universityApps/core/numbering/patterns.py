from enum import Enum
from unicodedata import numeric
from django.utils.translation import gettext_lazy as _

class NumberingPattern(Enum):
    NUMERIC = 'numeric'
    ALPHA = 'alpha'
    ALPHANUMERIC = 'alphanumeric'
    NAME_BASED = 'name_based'
    CUSTOM = 'custom'
    PARENT_BASED = 'parent_based'
    AdministrativedepartNumber = 'administrativedepartNumber'
    def label(self):
        labels = {
            'numeric': _("Numeric (e.g. 001, 002)"),
            'alpha': _("Alphabetic (e.g. A, B, C)"),
            'alphanumeric': _("Alphanumeric (e.g. A1, B2)"),
            'name_based': _("Based on name (e.g. CS, HR)"),
            'custom': _("Custom format"),
            'parent_based': _("Parent-based (e.g. 101, 102 for parent 1)"),
            'administrativedepartNumber': _("Numeric (e.g. 001, 002)"),
        }
        return labels.get(self.value, self.value)


class CodeFormatPattern(Enum):
    FIRST_LETTER_EACH_WORD = 'first_letter_each_word'
    FIRST_N_LETTERS = 'first_n_letters'
    FIRST_N_LETTERS_EACH_WORD = 'first_n_letters_each_word'
    ABBREVIATE_VOWELS_REMOVED = 'abbreviate_vowels_removed'
    MANUAL = 'manual'

    def label(self):
        return {
            'first_letter_each_word': _("First letter of each word"),
            'first_n_letters': _("First N letters of the first word"),
            'first_n_letters_each_word': _("First N letters of each word"),
            'abbreviate_vowels_removed': _("Abbreviated (vowels removed)"),
            'manual': _("Manual (user-provided code)")
        }.get(self.value, self.value)
