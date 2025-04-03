from textwrap import indent
from django.db import models
from django.utils.translation import gettext_lazy as _
from universityApps.core import numbering
from universityApps.core.numbering.department import DepartmentNumbering
from .utils import (
    department_image_path,
)


# نموذج اقسام الكليات 
class Department(models.Model):
    class DepartmentType(models.TextChoices):
        ACADEMIC = 'academic', _('Academic')
        ADMINISTRATIVE = 'administrative', _('Administrative')
    
    dept_no=models.IntegerField(
        editable=False,
        primary_key=True,
        serialize=False,
        verbose_name='Department Number',
        index=True
    )
    code = models.CharField(
        editable=False,
        help_text='Unique CODE for the department based on name',
        max_length=255,
        unique=True,
        verbose_name='Department Code',
    )
    name = models.CharField(
        help_text='Full name of the department',
        max_length=255,
        verbose_name='Department Name',
        help_text='Name of the department',
    )
    description = models.TextField(
        blank=True,
        help_text='Detailed description of the department',
        null=True,
        verbose_name='Department Description',
        help_text='Description of the department',
    )
    type = models.CharField(
        choices=DepartmentType.choices,
        default=DepartmentType.ACADEMIC,
        help_text='Type of the department',
        max_length=255,
        verbose_name='Department Type',
        help_text='Type of the department',
    )
    image = models.ImageField(
        blank=True,
        null=True,  
        upload_to=department_image_path,
        verbose_name='Department Image',
        help_text='Image of the department',
    )
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        verbose_name='College',
        help_text='College of the department',
    )
    depaertment_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Department Message',  
        help_text='Message of the department',
    )
    department_vision = models.TextField(
        blank=True,
        null=True,
        verbose_name='Department Vision',
        help_text='Vision of the department',
    )
    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['code', 'dept_no', 'name','college']
        indexes = [
            models.Index(fields=['dept_no', 'name'], name='department_dept_no_name_idx'),
            models.Index(fields=['college'], name='department_college_idx'),
            models.Index(fields=['code'], name='department_code_idx'),
        ]
    def save(self, *args, **kwargs):
        numbering = DepartmentNumbering()
        if not self.dept_no:
            if not self.code and self.name:
                self.code = numbering.generate_code(self.name, self.type)
            if self.type == self.DepartmentType.ACADEMIC and self.college:
                self.dep_no = numbering.generate_dep_no(college_id=self.college.college_no, type=self.type)
            else:
                
                # نمرر الاسم للقسم الإداري
                self.dep_no = numbering.generate_dep_no(type=self.type)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{str(self.dep_no).zfill(4)} – {self.name}"
