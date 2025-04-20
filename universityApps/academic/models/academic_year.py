"""Academic Year and Semester Models."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

class SEMESTER_TYPE(models.IntegerChoices):
    FIRST = 1, _('First')
    SECOND = 2, _('Second')
    SUMMER = 3, _('Summer')
class AcademicYear(models.Model):
    """Academic Year Model."""
    name=models.CharField(
        max_length=50,
        verbose_name=_("Academic Year Name"),
        help_text=_("Name of the academic year")
    )
    start_date=models.DateField(
        verbose_name=_("Start Date"),
        help_text=_("Start date of the academic year")
    )
    end_date=models.DateField(
        verbose_name=_("End Date"),
        help_text=_("End date of the academic year")
    )
    is_current = models.BooleanField(default=False, verbose_name=_("Is Current"), help_text=_("Whether the academic year is current"))
    created_at=models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"), help_text=_("Time when the academic year was created"))

    class Meta:
        verbose_name = _("Academic Year")
        verbose_name_plural = _("Academic Years")
        ordering = ['-start_date',]

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError({'start_date': _("Start date must be before end date")})
        if self.start_date < timezone.now().date():
            raise ValidationError({'start_date': _("Start date must be in the future")})
        if self.end_date < timezone.now().date():
            raise ValidationError({'end_date': _("End date must be in the future")})
        if self.is_current:
            """ Only one academic year can be current at a time """
            if AcademicYear.objects.filter(is_current=True).exclude(id=self.id).exists():
                raise ValidationError({'is_current': _("Only one academic year can be current at a time")})
            
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Semester(models.Model):
    """Semester Model."""

    academic_year=models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        verbose_name=_("Academic Year"),
        help_text=_("Academic year to which the semester belongs")
    )
    semester_type=models.CharField(
        max_length=50,
        choices=SEMESTER_TYPE.choices,
        verbose_name=_("Semester Type"),
        help_text=_("Type of the semester"))
    
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    
    end_date = models.DateField(
        verbose_name=_("End Date")
    )
    
    registration_start_date = models.DateField(
        verbose_name=_("Registration Start Date")
    )
    
    registration_end_date = models.DateField(
        verbose_name=_("Registration End Date")
    )
    final_exams_start_date = models.DateField(
        verbose_name=_("Final Exams Start Date")
    )
    
    final_exams_end_date = models.DateField(
        verbose_name=_("Final Exams End Date")
    )

    grades_due_date = models.DateField(
        verbose_name=_("Grades Due Date")
    )
    
    is_current = models.BooleanField(
        default=False,
        verbose_name=_("Is Current Semester")
    )

    class Meta:
        verbose_name = _("Semester")
        verbose_name_plural = _("Semesters")
        ordering = ['academic_year', 'start_date']
        unique_together = ['academic_year', 'semester_type']
        
    def __str__(self):
        return f"{self.academic_year} - {self.get_semester_type_display()}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({'start_date': _("Start date must be before end date")})
        if self.registration_start_date and self.registration_end_date and self.registration_start_date >= self.registration_end_date:
            raise ValidationError({'registration_start_date': _("Registration start date must be before end date")})
        if self.final_exams_start_date and self.final_exams_end_date and self.final_exams_start_date >= self.final_exams_end_date:
            raise ValidationError({'final_exams_start_date': _("Final exams start date must be before end date")})
        
        if self.is_current:
            """ Only one semester can be current at a time """
            if Semester.objects.filter(is_current=True).exclude(id=self.id).exists():
                raise ValidationError({'is_current': _("Another semester is already set as current")})
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        """Get the current semester"""
        try:
            return cls.objects.get(is_current=True)
        except cls.DoesNotExist:
            """If no current semester is found, return None"""
            today=timezone.now().date()
            try:
                return cls.objects.get(start_date__lte=today, end_date__gte=today)
            except cls.DoesNotExist:
                return None
            
    def is_registration_open(self):
        """Check if registration is open"""
        today = timezone.now().date()
        return self.registration_start_date <= today <= self.registration_end_date
    
    def is_final_exams_period(self):
        """Check if final exams period is open"""
        today = timezone.now().date()
        return self.final_exams_start_date <= today <= self.final_exams_end_date
