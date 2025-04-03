import re
from .base import BaseNumberingSystem
from .patterns import (
    NumberingPattern,
    CodeFormatPattern,
)

class CollegeNumbering:
    def __init__(self):
        from dynamic_preferences.registries import global_preferences_registry

        global_preferences = global_preferences_registry.manager()

        self.college_no_config = {
            'pattern': NumberingPattern(global_preferences['numbering__college_pattern']),
            'prefix': global_preferences['numbering__college_prefix'],
            'suffix': global_preferences['numbering__college_suffix'],
            'separator': global_preferences['numbering__college_separator'],
            'padding': global_preferences['numbering__college_padding'],
            'ignored_words': set(global_preferences['numbering__college_ignored_words'].split(','))
        }

        self.code_config = {
            'pattern': NumberingPattern.NAME_BASED,
            'ignored_words': set(global_preferences['numbering__college_ignored_words'].split(','))
        }
        self.code_format = global_preferences['numbering__college_code_format']
        self.code_length = global_preferences['numbering__college_code_length']


    def generate_college_no(self):
        from universityApps.colleges.models import College
        system = BaseNumberingSystem(**self.college_no_config)
        number = system.generate_number(
            model_class=College,
            field='college_no'
        )
        if  number < 10:
            number = '10'  # Ensure minimum number is 10
        return system.format_number(number)

    def generate_code(self, name):
        from universityApps.colleges.models import College
        system = BaseNumberingSystem(**self.code_config)
        return system.generate_number(
            model_class=College,
            name=name,
            field='code',
            code_format=self.code_format,
            code_length=self.code_length,
        )
