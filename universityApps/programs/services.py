from os import name
from universityApps.academic.models.academic_year import SEMESTER_TYPE
from .models import ProgramSettings, AcademicLevel
from universityApps.academic.models import SemesterPlan, StudyPlan
from django.utils import timezone
LEVEL_NAMES_AR = {
    1: "المستوى الأول",
    2: "المستوى الثاني",
    3: "المستوى الثالث",
    4: "المستوى الرابع",
    5: "المستوى الخامس",
    6: "المستوى السادس",
    7: "المستوى السابع",
}

LEVEL_NAMES_EN = {
    1: "First Level",
    2: "Second Level",
    3: "Third Level",
    4: "Fourth Level",
    5: "Fifth Level",
    6: "Sixth Level",
    7: "Seventh Level",
}

SEMESTER_NAMES = {
    1: ("الفصل الأول", "First Semester"),
    2: ("الفصل الثاني", "Second Semester"),
}

def create_program_settings_for_program(program, standard_duration_years=4.0):
    """
    إنشاء ProgramSettings تلقائيًا لبرنامج أكاديمي جديد.
    """
    if not program:
        raise ValueError("Program instance must be provided.")

    ProgramSettings.objects.get_or_create(
        program=program,
        defaults={
            'standard_duration_years': standard_duration_years,
            'max_duration_years': standard_duration_years + 2,
            'credits_per_semester': 18,
            'min_credits_per_semester': 12,
            'max_credits_per_semester': 24,
            'summer_semester_enabled': False,
            'max_summer_credits': 12,
            'min_cgpa_required': 65.00,
        }
    )

def create_program_structure(program):
    """
    إنشاء المستويات الأكاديمية بناءً على standard_duration_years من إعدادات البرنامج.
    """
    if not program:
        raise ValueError("Program instance must be provided.")

    settings = getattr(program, 'programsettings', None)
    if not settings:
        raise ValueError("ProgramSettings must exist for the program.")

    total_semesters  = settings.calculate_total_semesters()
    total_levels = total_semesters // 2

    # create Study Plan
    study_plan ,_= StudyPlan.objects.get_or_create(
        program=program,
        version=1,
        defaults={
            'name': f"{program.name} Study Plan",
            'status': StudyPlan.Status.Active,
            'effective_from': timezone.now().date(),  # Set the effective date to the current date
        }
    )
    required_credits = settings.credits_per_semester * 2
    # create Academic Levels
    for level_num in range(1, total_levels + 1):
        name_ar = LEVEL_NAMES_AR.get(level_num, f"المستوى {level_num}")
        name_en = LEVEL_NAMES_EN.get(level_num, f"Level {level_num}")

        level ,_ = AcademicLevel.objects.get_or_create(
            program=program,
            level_number=level_num,
            defaults={
                'name_ar': name_ar,
                'name_en': name_en,
                'required_credits': required_credits,
            }
        )

        # create Semester Plans
        for semester_type in [SEMESTER_TYPE.FIRST, SEMESTER_TYPE.SECOND]:
            sem_ar ,sem_en = SEMESTER_NAMES[semester_type]
            order = (level.level_number - 1) * 2 + semester_type
            SemesterPlan.objects.get_or_create(
                study_plan=study_plan,
                academic_level=level,
                semester_type=semester_type,
                defaults={
                    'name_ar':  sem_ar,
                    'name_en': sem_en,
                    'order': order
                }
            )