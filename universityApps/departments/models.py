from django.db import models
from django.utils.translation import gettext_lazy as _
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
        verbose_name=_('Department Number'),
        db_index=True
    )
    code = models.CharField(
        editable=False,
        help_text=_('Code (automatically generated from name)'),    
        max_length=255,
        unique=True,
        verbose_name=_('Department Code'),
    )
    head=models.ForeignKey(
        'users.FacultyMember',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_head',
        verbose_name=_('Head of the Department'),
        help_text=_('Head of the department'),
    )
    name = models.CharField(
        help_text=_('Name of the department'),
        max_length=255,
        verbose_name=_('Department Name'),
    )
    description = models.TextField(
        blank=True,
        help_text=_('Description of the department'),
        null=True,
        verbose_name='Department Description',
    )
    type = models.CharField(
        choices=DepartmentType.choices,
        max_length=255,
        verbose_name=_('Department Type'),
        help_text=_('Type of the department'),
    )
    image = models.ImageField(
        blank=True,
        null=True, 
        upload_to=department_image_path,
        verbose_name=_('Department Image'),
        help_text=_('Image of the department'),
    )
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        verbose_name=_('College'),
        help_text=_('College to which the department belongs'),
    )
    depaertment_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Department Message'),
        help_text=_('Message to be displayed on the department page'),
        )
    department_vision = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Department Vision'),
        help_text=_('Vision of the department'),
    )
    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['code', 'dept_no', 'name','college','type']
        indexes = [
            models.Index(fields=['dept_no', 'name'], name='department_dept_no_name_idx'),
            models.Index(fields=['college'], name='department_college_idx'),
            models.Index(fields=['code'], name='department_code_idx'),
            models.Index(fields=['type'], name='department_type_index'),
        ]
    def save(self, *args, **kwargs):
        numbering = DepartmentNumbering()
        if not self.dept_no:
            if not self.code and self.name:
                self.code = numbering.generate_code(self.name, self.type)
            if self.type == self.DepartmentType.ACADEMIC and self.college:
                self.dept_no = numbering.generate_dept_no(college_id=self.college.college_no, type=self.type)
            else:
                
                # نمرر الاسم للقسم الإداري
                self.dept_no = numbering.generate_dept_no(type=self.type)
        super().save(*args, **kwargs)
    def is_head(self, faculty_member):
        # Check if the given faculty member is the head of the department
        return self.head == faculty_member
    def __str__(self):
        return f"{str(self.dept_no).zfill(4)} – {self.name}"
