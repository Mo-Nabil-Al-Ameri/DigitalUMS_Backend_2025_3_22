from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference, ChoicePreference, Section, IntegerPreference
from django.utils.translation import gettext_lazy as _
from .numbering.patterns import (NumberingPattern, CodeFormatPattern)

numbering = Section('numbering')


# ========= College Settings =========

@global_preferences_registry.register
class CollegePattern(ChoicePreference):
    section = numbering
    name = 'college_pattern'
    choices = [(p.value, p.label()) for p in NumberingPattern]
    default = NumberingPattern.NUMERIC.value
    verbose_name = _("College Numbering Pattern")

@global_preferences_registry.register
class CollegePrefix(StringPreference):
    section = numbering
    name = 'college_prefix'
    default = ''
    verbose_name = _("College Prefix")

@global_preferences_registry.register
class CollegeSuffix(StringPreference):
    section = numbering
    name = 'college_suffix'
    default = ''
    verbose_name = _("College Suffix")

@global_preferences_registry.register
class CollegeSeparator(StringPreference):
    section = numbering
    name = 'college_separator'
    default = ''
    verbose_name = _("College Separator")

@global_preferences_registry.register
class CollegePadding(IntegerPreference):
    section = numbering
    name = 'college_padding'
    default = 2
    verbose_name = _("College Padding")

@global_preferences_registry.register
class CollegeIgnoredWords(StringPreference):
    section = numbering
    name = 'college_ignored_words'
    default = 'and,of,the,في,من,ال,و'
    verbose_name = _("College Ignored Words")

@global_preferences_registry.register
class CollegeCodeFormat(ChoicePreference):
    section = numbering
    name = 'college_code_format'
    choices = [(p.value, p.label()) for p in CodeFormatPattern]
    default = CodeFormatPattern.FIRST_LETTER_EACH_WORD.value
    verbose_name = _("College Code Format")

@global_preferences_registry.register
class CollegeCodeLength(IntegerPreference):
    section = numbering
    name = 'college_code_length'
    default = 3
    verbose_name = _("Number of letters for college code")


# ========= Department Settings =========

@global_preferences_registry.register
class DepartmentPattern(ChoicePreference):
    section = numbering
    name = 'department_pattern'
    choices = [(p.value, p.label()) for p in NumberingPattern]
    default = NumberingPattern.PARENT_BASED.value
    verbose_name = _("Department Numbering Pattern")

@global_preferences_registry.register
class DepartmentPrefix(StringPreference):
    section = numbering
    name = 'department_prefix'
    default = ''
    verbose_name = _("Department Prefix")

@global_preferences_registry.register
class DepartmentSuffix(StringPreference):
    section = numbering
    name = 'department_suffix'
    default = ''
    verbose_name = _("Department Suffix")

@global_preferences_registry.register
class DepartmentSeparator(StringPreference):
    section = numbering
    name = 'department_separator'
    default = '_'
    verbose_name = _("Department Separator")

@global_preferences_registry.register
class DepartmentPadding(IntegerPreference):
    section = numbering
    name = 'department_padding'
    default = 3
    verbose_name = _("Department Padding")

@global_preferences_registry.register
class DepartmentIgnoredWords(StringPreference):
    section = numbering
    name = 'department_ignored_words'
    default = 'and,of,the,في,من,ال,و'
    verbose_name = _("Department Ignored Words")

@global_preferences_registry.register
class DepartmentCodeFormat(ChoicePreference):
    section = numbering
    name = 'department_code_format'
    choices = [(p.value, p.label()) for p in CodeFormatPattern]
    default = CodeFormatPattern.FIRST_LETTER_EACH_WORD.value
    verbose_name = _("Department Code Format")

@global_preferences_registry.register
class DepartmentCodeLength(IntegerPreference):
    section = numbering
    name = 'department_code_length'
    default = 2
    verbose_name = _("Number of letters for department code")

@global_preferences_registry.register
class DepartmentAcademicSuffix(StringPreference):
    section = numbering
    name = 'department_academic_suffix'
    default = '-A'
    verbose_name = _("Academic Department Code Suffix")

@global_preferences_registry.register
class DepartmentAdministrativeSuffix(StringPreference):
    section = numbering
    name = 'department_admin_suffix'
    default = '-I'
    verbose_name = _("Administrative Department Code Suffix")
@global_preferences_registry.register
class DepartmentAcademicMinNumber(IntegerPreference):
    section = numbering
    name = 'department_academic_min_number'
    default = 1000
    verbose_name = _("Academic Department Min Number")

@global_preferences_registry.register
class DepartmentAcademicMaxNumber(IntegerPreference):
    section = numbering
    name = 'department_academic_max_number'
    default = 9999
    verbose_name = _("Academic Department Max Number")


# ========= Administrative Department Settings =========
@global_preferences_registry.register
class AdministrativeDepartmentPrefix(StringPreference):
    section = numbering
    name = 'department_admin_prefix'
    default = 'ADM'
    verbose_name = _("Administrative Department Prefix")
@global_preferences_registry.register
class DepartmentAdminMinNumber(IntegerPreference):
    section = numbering
    name = 'department_admin_min_number'
    default = 1
    verbose_name = _("Administrative Department Min Number")

@global_preferences_registry.register
class DepartmentAdminMaxNumber(IntegerPreference):
    section = numbering
    name = 'department_admin_max_number'
    default = 999
    verbose_name = _("Administrative Department Max Number")
@global_preferences_registry.register
class DepartmentAdminMinNumber(IntegerPreference):
    section = numbering
    name = 'department_admin_min_number'
    default = 1
    verbose_name = _("Administrative Department Min Number")

@global_preferences_registry.register
class DepartmentAdminMaxNumber(IntegerPreference):
    section = numbering
    name = 'department_admin_max_number'
    default = 999
    verbose_name = _("Administrative Department Max Number")
