from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Sum
class StudyPlan(models.Model):
    """Study Plan Model."""
    class Status(models.TextChoices):
        Draft = 'draft', _('Draft')
        Active = 'active', _('Active')
        Archived = 'archived', _('Archived')

    program = models.ForeignKey(
        'programs.AcademicProgram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_plans',
        verbose_name=_("Program"),
        help_text=_("Program to which the study plan belongs")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"), help_text=_("Name of the study plan"),editable=False)
    version = models.PositiveSmallIntegerField(verbose_name=_("Version"), default=1)
    status = models.CharField(max_length=20, verbose_name=_("Status"), choices=Status.choices, default=Status.Draft)
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    effective_from = models.DateField(verbose_name=_("Effective Date"),)

    class Meta:
        verbose_name = _("Study Plan")
        verbose_name_plural = _("Study Plans")
        unique_together =[ 'program', 'version']
        ordering = ['-effective_from', 'version']
        indexes = [
            models.Index(fields=['status'], name='study_plan_status_idx'),
            models.Index(fields=['effective_from'], name='study_plan_effective_from_idx'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.program.name} Study Plan"
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} - Version {self.version}"
    

class SemesterPlan(models.Model):
    from .academic_year import SEMESTER_TYPE

    study_plan = models.ForeignKey(
        StudyPlan, 
        on_delete=models.CASCADE,
        related_name='Plan_semester_plans',
        verbose_name=_("Study Plan"),
        help_text=_("Study plan to which the semester plan belongs")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"), help_text=_("Name of the semester plan"),editable=False)
    semester_type=models.IntegerField(
        choices=SEMESTER_TYPE.choices,
        verbose_name=_("Semester Type"),
        help_text=_("Type of the semester")
    )
    order = models.PositiveSmallIntegerField(verbose_name=_("Order"), help_text=_("Order of the semester plan"),editable=False)
    academic_level = models.ForeignKey(
        'programs.AcademicLevel',
        on_delete=models.CASCADE,
        related_name='semester_plans',
        verbose_name=_("Academic Level"),
        help_text=_("Academic level to which the semester plan belongs")
    )
    recommended_credits = models.PositiveIntegerField(
        default=15,
        verbose_name=_("Recommended Credits"),
        help_text=_("Recommended number of credits for this semester")
    )
    
    min_credits = models.PositiveIntegerField(
        default=12,
        verbose_name=_("Minimum Credits"),
        help_text=_("Minimum number of credits required for this semester")
    )
    
    max_credits = models.PositiveIntegerField(
        default=18,
        verbose_name=_("Maximum Credits"),
        help_text=_("Maximum number of credits allowed for this semester")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )

    class Meta:
        verbose_name = _("Semester Plan")
        verbose_name_plural = _("Semester Plans")
        unique_together = ['study_plan', 'academic_level', 'semester_type']
        ordering = ['academic_level', 'semester_type']
        indexes = [
            models.Index(fields=['academic_level'], name='semester_plan_level_idx'),
            models.Index(fields=['semester_type'], name='semester_plan_type_idx'),
        ]
    def __str__(self):
        return f" {self.academic_level} - {self.name}"

    def clean(self):
        # validate that the academic level is in the same program as the study plan
        if self.academic_level.program != self.study_plan.program:
            raise ValidationError({
                'academic_level': _("Academic level must belong to the same program as the study plan")
            })
        
        # check the range of credits
        if self.min_credits > self.max_credits:
            raise ValidationError({
                'min_credits': _("Minimum credits cannot be greater than maximum credits")
            })
        
        if self.recommended_credits < self.min_credits or self.recommended_credits > self.max_credits:
            raise ValidationError({
                'recommended_credits': _("Recommended credits must be between minimum and maximum credits")
            })
    
    def  save(self, *args, **kwargs):
        """Save the semester plan with validation"""
        self.order = (self.academic_level.level_number - 1) * 2 + self.semester_type
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_total_credits(self):
        """Calculate the total credits hours for Courses at this level"""
        total_credits =self.semester_courses.aggregate(Sum('course__credits'))['course__credits__sum'] or 0
        return total_credits
    
    def get_required_credits(self):
        """Calculate the required credits hours for Courses at this level"""
        required_credits =self.semester_courses.filter(is_required=True).aggregate(Sum('course__credits'))['course__credits__sum'] or 0
        return required_credits
    
    def get_elective_credits(self):
        """Calculate the elective credits hours for Courses at this level"""
        elective_credits =self.semester_courses.filter(is_required=False).aggregate(Sum('course__credits'))['course__credits__sum'] or 0
        return elective_credits
    
    def map_to_academic_semester(self, academic_year):
        """Map the semester plan to an academic semester"""
        from .academic_year import Semester
        # search for the appropriate academic semester  in the given academic year
        try:
            academic_semester = Semester.objects.get(academic_year=academic_year, semester_type=self.semester_type)
            return academic_semester
        except Semester.DoesNotExist:
            return None
        

class SemesterCourse(models.Model):
    from universityApps.courses.fields import OrderField
    semester_plan = models.ForeignKey(
        SemesterPlan,
        on_delete=models.CASCADE,
        related_name='semester_courses',
        verbose_name=_("Semester Plan"),
        help_text=_("Semester plan to which the semester course belongs")
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='course_semester',
        verbose_name=_("Course"),
        help_text=_("Course to which the semester course belongs")
    )
    order = OrderField(blank=True,for_fields=['semester_plan'])
    is_required = models.BooleanField(default=True, verbose_name=_("Required"), help_text=_("Is the course required for the semester plan?"))
    code=models.CharField( verbose_name=_("Code"), help_text=_("Code of the course"), editable=False,blank=True, null=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When the semester course was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("When the semester course was last updated")
    )
    class Meta:
        verbose_name = _("Semester Course")
        verbose_name_plural = _("Semester Courses")
        unique_together = ['semester_plan', 'course']
        ordering =['semester_plan', 'order',]
        indexes = [
            models.Index(fields=['semester_plan'], name='semester_course_plan_idx'),
            models.Index(fields=['order'], name='semester_course_order_idx'),
            models.Index(fields=['is_required'], name='semester_course_required_idx'),
        ]

    def clean(self):

        existing= SemesterCourse.objects.filter(
            semester_plan__study_plan=self.semester_plan.study_plan,
            course=self.course,
        ).exclude(id=self.id)

        if existing.exists():
            raise ValidationError({
                'course': _("Course already exists in this study plan")
            })
        # check course prerequisites        
        prerequisites = self.course.get_all_prerequisites(include_indirect=True)
        if prerequisites:
            # check that all prerequisites are in previous semesters
            current_semester_order =self.semester_plan.order
            for prereq in prerequisites:
                # search for prerequisites in semesters Plan
                prereq_courses = SemesterCourse.objects.filter(
                    semester_plan__study_plan=self.semester_plan.study_plan,
                    course=prereq)
                if not prereq_courses.exists():
                    

                    continue # skip if not found

                for prereq_course in prereq_courses:
                    if prereq_course.semester_plan.order >= current_semester_order:
                        raise ValidationError({
                            'course': _("Prerequisites %(prereq)s must be in an earlier semesters")% {
                                'prereq': prereq.code
                            }

                        })
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if self.id:
         if not self.code:
            self.code = f"{self.course.subject.code}{self.semester_plan.academic_level.level_number}{self.semester_plan.semester_type}{self.order}"
            super().save(update_fields=['code'])

    def get_actual_semester(self, academic_year):
        """Get the actual semester for this course in the given academic year"""
        actual_semester = self.semester_plan.map_to_academic_semester(academic_year)
        return actual_semester
    def __str__(self):
        return f"{self.semester_plan} - {self.code}"
        