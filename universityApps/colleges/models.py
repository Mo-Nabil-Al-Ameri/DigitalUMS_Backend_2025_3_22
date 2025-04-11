from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.core.exceptions import ValidationError
from universityApps.core.numbering.college import CollegeNumbering
# نموذج الكليات 
class College(models.Model):
    college_no=models.IntegerField(
        primary_key=True,
        verbose_name=_("College Number"),
        editable=False
    )
    university=models.ForeignKey(
        "core.University",
        on_delete=models.CASCADE,verbose_name=_("University")
        )
    code = models.CharField(
        unique=True,
        verbose_name=_("College Code"),
        editable=False,  # لمنع التعديل اليدوي
        help_text=_("code (automatically generated from name")
    )
    dean=models.ForeignKey(
        "users.FacultyMember",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Dean"),
        help_text=_("Dean of the college")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("College Name"),
        help_text=_("Full name of the college")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("College Description"),
        help_text=_("Detailed description of the college")
    )
    
    class Meta:
        verbose_name = _("College")
        verbose_name_plural = _("Colleges")
        ordering = ['code','college_no']
        indexes = [
            models.Index(fields=['college_no', 'name'], name='college_college_no_name_idx'),
        ]
    def save(self, *args, **kwargs):
        numbering = CollegeNumbering()
        if not self.college_no:
            # توليد رقم الكلية إذا كان جديداً
            self.college_no = numbering.generate_college_no()

        if  self.name and not self.code:
            self.code = numbering.generate_code(self.name)
        super().save(*args, **kwargs)

    def is_dean(self, faculty_member):
        # check if the given faculty member is the dean of this college
        return self.dean == faculty_member
    def __str__(self):
        return  f" {self.code}-{self.name}"

