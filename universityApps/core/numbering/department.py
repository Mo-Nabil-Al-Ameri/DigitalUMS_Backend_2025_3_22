from ast import pattern
import code
import sys
from django.forms import ValidationError
from .base import BaseNumberingSystem
from .patterns import (
    NumberingPattern,
    CodeFormatPattern,
)

class DepartmentNumbering:
    def __init__(self):
        from dynamic_preferences.registries import global_preferences_registry
        global_preferences = global_preferences_registry.manager()

        # إعدادات رقم القسم
        self.dept_no_config = {
            'pattern': NumberingPattern(global_preferences['numbering__department_pattern']),
            'prefix': global_preferences['numbering__department_prefix'],
            'suffix': global_preferences['numbering__department_suffix'],
            'separator': global_preferences['numbering__department_separator'],
            'padding': global_preferences['numbering__department_padding'],
            'ignored_words': set(global_preferences['numbering__department_ignored_words'].split(','))
        }

        # إعدادات الكود
        self.code_config = {
            'pattern': NumberingPattern.NAME_BASED,
            'ignored_words': set(global_preferences['numbering__department_ignored_words'].split(','))
        }
        self.code_format =CodeFormatPattern(global_preferences['numbering__department_code_format']), 
        self.code_length = global_preferences['numbering__department_code_length']

        # بادئات ولاحقات حسب النوع
        self.academic_suffix = global_preferences['numbering__department_academic_suffix']
        self.admin_suffix = global_preferences['numbering__department_admin_suffix']
        self.admin_prefix = global_preferences['numbering__department_admin_prefix']
        self.academic_min  = global_preferences['numbering__department_academic_min_number']
        self.academic_max =global_preferences['numbering__department_academic_max_number']
        self.admin_min = global_preferences['numbering__department_admin_min_number']
        self.admin_max = global_preferences['numbering__department_admin_max_number']

    def generate_dept_no(self, college_id=None, type=None):
        from universityApps.departments.models import Department
        system = BaseNumberingSystem(**self.dept_no_config)

        if type == 'academic' and college_id:
            system.min_value =  self.academic_min
            system.max_value = self.academic_max
            return system.generate_number(
                model_class=Department,
                parent_field='college',
                parent_id=college_id,
                field='dept_no'
            )

        elif type == 'administrative':
            system.pattern =NumberingPattern.numeric2
            system.min_value = self.admin_min     # 0001
            system.max_value = self.admin_max    # 0999
            return system.generate_number(
                model_class=Department,
                field='dept_no',
                filters={'type': 'administrative'}  # ✅ التصفية حسب النوع
            )

        else:
            raise ValidationError("Invalid department type or missing college_id.")
    def generate_code(self, name, type):
        from universityApps.departments.models import Department
        system = BaseNumberingSystem(**self.code_config)
        return system.generate_number(
            model_class=Department,
            name=name,
            type=type,
            field='code',
            academic_suffix=self.academic_suffix,
            admin_suffix=self.admin_suffix
        )
    def generate_program_no(self, department_id=None, type=None):
        from universityApps.programs.models import AcademicProgram
        system = BaseNumberingSystem(**self.dept_no_config)
        return system.generate_number(
            model_class=AcademicProgram,
            parent_field='department',
            parent_id=department_id,
            field='program_no'
        )