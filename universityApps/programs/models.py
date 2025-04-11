from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import Sum
from universityApps.courses.fields import OrderField
from django.apps import apps
class StudySystem(models.TextChoices):
        FULL_TIME = 'Full_Time', _('Full Time')
        PART_TIME = 'Part_Time', _('Part Time')
        DISTANCE = 'Distance', _('Distance Learning')
        BLENDED = 'Blended', _('Blended Learning') 
class AcademicProgram(models.Model):
    """Academic program model according to the Bologna process criteria"""
    class DegreeLevel(models.TextChoices):
        DIPLOMA = 'Diploma', _('Diploma')
        BACHELOR = 'Bachelor', _('Bachelor\'s')
        MASTER = 'Master', _('Master\'s')
        PHd = 'phD', _('phD')

    program_no=models.IntegerField(
        editable=False, 
        unique=True,
        index=True,
        help_text=_('Unique numeric identifier for the program based on program\'s department'),
        verbose_name=_("Program Number"))
    code = models.CharField(
        unique=True,
        verbose_name=_("Program Code"),
        editable=False,  # لمنع التعديل اليدوي
        help_text=_("code (automatically generated from name")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Program Name"),
        help_text=_("Full name of the program")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Program Description"),
        help_text=_("Detailed description of the program")
    )
    degree_level = models.CharField(
        choices=DegreeLevel.choices,
        max_length=15,
        default=DegreeLevel.BACHELOR,
        verbose_name=_("Degree Level"),
        help_text=_("Degree level of the program")
    )
    study_system = models.CharField(
        choices=StudySystem.choices,
        max_length=15,
        default=StudySystem.BLENDED,
        verbose_name=_("Study System"),
        help_text=_("Study system of the program")
    )
    total_credits = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Total Credits"),
        help_text=_("Total number of credits for the program")
    )
    learning_outcomes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Learning Outcomes"),
        help_text=_("Program learning outcomes according to Bologna standards")
    )
    admission_requirements = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Admission Requirements")
    )
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default='ar',
        verbose_name=_("Teaching Language"),
        help_text=_("Language of instruction for the program")
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='programs',
        verbose_name=_("Department"),
        help_text=_("Department of the program")
    )
    class Meta:
        verbose_name = _("Academic Program")
        unique_together = ('department', 'degree_level')
        verbose_name_plural = _("Academic Programs")
        ordering = ['code', 'program_no','degree_level']
        indexes = [
             models.Index(fields=['code'], name='program_code_idx'),
             models.Index(fields=['department'], name='program_department_idx'),
             models.Index(fields=['degree_level'], name='program_degree_level_idx'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProgramSettings(models.Model):
    """ Settings for an academic program """
    program = models.OneToOneField(
        AcademicProgram,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_("Program"),
        help_text=_("Program to which the settings belong")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether the program is active or not")
    )
    #duration and semesters settings
    standard_duration_years = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_("Duration"),
        help_text=_("Standard duration to complete the program in years")
    )
    max_duration_years = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        verbose_name=_("Maximum Duration Years"),   
        help_text=_("Maximum allowed duration to complete the program in years")
    )
    credits_per_semester = models.PositiveSmallIntegerField(
        default=18,
        verbose_name=_("Credits per Semester"),
        help_text=_("Number of credits required per semester")
    )
    min_credits_per_semester = models.PositiveSmallIntegerField(
        default=12,
        verbose_name=_("Minimum Credits per Semester"),
        help_text=_("Minimum number of credits required per semester")
    )
    max_credits_per_semester = models.PositiveSmallIntegerField(
        default=24,
        verbose_name=_("Maximum Credits per Semester"),
        help_text=_("Maximum number of credits allowed per semester")
    )
    summer_semester_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Summer Semester Enabled"),
        help_text=_("Whether summer semester is enabled or not")
    )
    max_summer_credits = models.PositiveSmallIntegerField(
        default=12,
        verbose_name=_("Maximum Summer Credits"),
        help_text=_("Maximum number of credits allowed for the summer semester")
    )

    #Graduation rquirement 
    min_cgpa_required = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.5,
        verbose_name=_("Minimum CGPA"),
        help_text=_("Minimum CGPA required to graduate")
    )
    class Meta:
        verbose_name = _("Program Settings")
        verbose_name_plural = _("Program Settings")

    def __str__(self):
        return f"Settings for {self.program.name}"
    
    def clean(self):
        # validate duration years
        if self.max_duration_years < self.standard_duration_years:
            raise ValidationError(
                {'max_duration_years':_("Maximum duration years must be greater than standard duration years")}
            )
        if self.min_credits_per_semester > self.max_credits_per_semester:
            raise ValidationError(
                {'min_credits_per_semester':_("Minimum credits of a semester must be less than maximum credits")}
            )
    
    def calculate_total_semesters(self):
        """calculate total number of semesters"""
        years=float(self.standard_duration_years)
        semesters_per_year=3 if self.summer_semester_enabled else 2
        return int(years*semesters_per_year)
    
    def calculate_total_credits(self):
        """calculate total number of credits"""
        return self.credits_per_semester * self.calculate_total_semesters()
    
    def validate_semesters_credits(self, credits, semester_type='regular'):
        """validate semesters and credits"""
        if semester_type == "summer":
            if credits > self.max_summer_credits:
                raise ValidationError(
                    {'max_summer_credits':_("Summer semester credits cannot exceed %(max)s")},
                    params={'max':self.max_summer_credits}
                )
        else:
            if credits < self.min_credits_per_semester:
                raise ValidationError(
                    {'min_credits_per_semester':_("Regular semester credits cannot be less than %(min)s")},
                    params={'min':self.min_credits_per_semester}
                )
            if credits > self.max_credits_per_semester:
                raise ValidationError(
                    {'max_credits_per_semester':_("Regular semester credits cannot exceed %(max)s")},
                    params={'max':self.max_credits_per_semester}
                )
            
# Academic Level Model 
class AcademicLevel(models.Model):
    """ Academic level model """

    program = models.ForeignKey(
        AcademicProgram,
        on_delete=models.CASCADE,
        verbose_name=_("Program"),
        help_text=_("Program to which the level belongs")
    )
    level_number = OrderField(
        unique=True,
        blank=True,
        editable=False,
        for_fields=['program'],
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Level Name"),
        help_text=_("Name of the level")
    )
    required_credits = models.PositiveSmallIntegerField(
        verbose_name=_("Required Credits"),
        help_text=_("Required credits to complete this level")
    )
    prerequisite_level = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='next_levels',
        verbose_name=_("Prerequisite Level"),
        help_text=_("Level that must be completed before this level")
    )
    class Meta:
        verbose_name = _("Academic Level")
        verbose_name_plural = _("Academic Levels")
        ordering = ['level_number', 'program']
        unique_together = ('program', 'level_number')
        indexes = [
            models.Index(fields=['program', 'level_number'], name='academic_level_program_level_number_idx'),
        ]

    def __str__(self):
        return f"{self.program.name} - {self.name} (Level {self.level_number})"

    #
    def clean(self):
        """Validate academic level data"""
        super().clean()

        # validate that the prerequisite level is lower than the current level
        if self.prerequisite_level and self.prerequisite_level.level_number >= self.level_number:
            raise ValidationError({
                'prerequisite_level': _("Prerequisite level must be lower than the current level")
            })
        # validate that the prerequisite level belongs to the same program
        if self.prerequisite_level and self.prerequisite_level.program != self.program:
            raise ValidationError({
                'prerequisite_level': _("Prerequisite level must belong to the same program")
            })
    
    def save(self, *args, **kwargs):
        """Save the academic level with validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_total_credits(self):
        """Calculate the total credits hours for Courses at this level"""
        return self.semester_plans.aggregate(
            total_credits=Sum(models.F('semester_courses__course__credits'))
            )['total_credits'] or 0

    def get_semesters(self):
        """get the semesters of this level"""
        semesters=self.semester_plans.all().order_by('year','semester_type')
        return semesters
    
    def get_courses(self):
        """get all courses at this level"""
        from django.db.models import Prefetch

        Course=apps.get_model('universityApps.courses','Course')
        SemesterCourse = apps.get_model('universityApps.academic', 'SemesterCourse')

        semestercourse_qs=SemesterCourse.objects.filter(
            semester_plan__academic_level=self
            )
        return Course.objects.filter(
            semester_courses__in=semestercourse_qs
        ).distinct().prefetch_related(
            Prefetch('semester_courses', queryset=semestercourse_qs)
        )
# اشتغل على تطبيق academic اول ما تبداء بكرة 
