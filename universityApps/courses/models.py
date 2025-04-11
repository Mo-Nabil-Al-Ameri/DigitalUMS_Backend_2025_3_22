from argparse import OPTIONAL
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .fields import OrderField
from .utils import (
    generate_unique_code,
    generate_unique_slug,
    )
User = get_user_model()
class Subject(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_("Subject Name"),
        help_text=_("Name of the subject")
        )
    slug=models.SlugField(
        unique=True,
        verbose_name=_("Subject Slug"),
        max_length=250,
        help_text=_("Slug of the subject"),
        editable=False,
    )
    
    code = models.CharField(
        unique=True,
        verbose_name=_("Subject Code"),
        max_length=50,
        help_text=_("Code of the subject"),
        editable=False,
    )

    @property
    def total_courses(self) -> int:
        return self.courses.count()

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        ordering = ["name", "code"]
        indexes = [
            models.Index(fields=["code"], name="subject_code_idx"),
            models.Index(fields=["slug"], name="subject_slug_idx"),
        ]
    def get_absolute_url(self):
        return reverse("subject_detail", kwargs={"slug": self.slug})
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code(
                model=Subject,
                instance=self,
                from_field='name',
                field_name='code',
                max_check=20
            )
        if not self.slug:
            self.slug = generate_unique_slug(
                model=Subject,
                instance=self,
                slug_field_name='slug',
                slug_from_fields=['code','name'],
                max_check=10
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Course(models.Model):
    class COURSE_TYPES(models.TextChoices):
       MANDATORY = 'mandatory', _('mandatory')
       ELECTIVE = 'elective', _('elective')
       OPTIONAL = 'optional', _('optional')

    class COURSE_GROUPS(models.TextChoices):
        UNIVERSITY='university',_('university Requirements')
        COLLEGE='college',_('college Requirements')
        PROGRAM='program',_('program Requirements')
        SPECIALIZATION='specialization',_('specialization Requirements')

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name=_("Subject"),
        help_text=_("Subject of the course")
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_("Course Name"),
        help_text=_("Name of the course")
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Course Slug"),
        max_length=250,
        help_text=_("Slug of the course"),
        editable=False,
    )
    credits = models.PositiveSmallIntegerField(
        verbose_name=_("Credits"),
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        help_text=_("Number of credits for the course"),
    )
    hours_lecture = models.PositiveSmallIntegerField(
        verbose_name=_("Lecture Hours"),
        validators=[MinValueValidator(1)],
        help_text=_("Number of lecture hours for the course"),
    )
    hours_lab = models.PositiveSmallIntegerField(
        verbose_name=_("Lab Hours"),
        validators=[MinValueValidator(1)],
        help_text=_("Number of lab hours for the course"),
    )
    practice_hours = models.PositiveSmallIntegerField(
        verbose_name=_("Practice Hours"),
        validators=[MinValueValidator(1)],
        help_text=_("Number of practice hours for the course"),
    )
    code = models.CharField(
        unique=True,
        verbose_name=_("Course Code"),
        max_length=50,
        help_text=_("Code of the course"),
        editable=False,
    )

    course_type = models.CharField(
        max_length=20,
        default=COURSE_TYPES.MANDATORY,
        choices=COURSE_TYPES.choices,
        verbose_name=_("Course Type"),
        help_text=_("Type of the course")
    )
    course_group = models.CharField(
        max_length=20,
        default=COURSE_GROUPS.UNIVERSITY,
        choices=COURSE_GROUPS.choices,
        verbose_name=_("Course Group"),
        help_text=_("Group of the course")
    )
    overview = models.TextField(
        verbose_name=_("Overview"),
        help_text=_("Overview of the course")
    )
    prerequisites =models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name=_("Prerequisites"),
        help_text=_("Prerequisites for the course"),
        related_name='prerequisite_for',
    )
    corequisites =models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name=_("Corequisites"),
        help_text=_("Corequisites for the course"),
        related_name='corequisite_for',
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'type': 'academic'},
        verbose_name=_("Department"),
        help_text=_("Department of the course"),
        related_name='department_courses',
    )
    is_active=models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether the course is active or not")
    )
    syllabus_file = models.FileField(
        upload_to='syllabi/',
        null=True,
        blank=True,
        verbose_name=_("Syllabus File")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When the course was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("When the course was last updated")
    )
    learning_outcomes = models.TextField(
        verbose_name=_("Learning Outcomes"),
        help_text=_("Learning outcomes for the course")
    )
    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ["-created_at", "code"]
        indexes = [
            models.Index(fields=['code'], name='course_code_idx'),
            models.Index(fields=['course_type'], name='course_type_idx'),
            models.Index(fields=['subject'], name='course_subject_idx'),
            models.Index(fields=['slug'], name='course_slug_idx'),
            models.Index(fields=['department','is_active'], name='course_department_idx'),
        ]
    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def clean(self):
        """ validate course data """
        super().clean()
        if not self.code:
            self.code = generate_unique_code(
                model=Course,
                instance=self,
                field_name='code',
                from_field=self.department.code,
                max_check=50
            )
        if not self.slug:
            self.slug = generate_unique_slug(
                model=Course,
                instance=self,
                slug_field_name='slug',
                slug_from_fields=['code','name'],
                max_check=50
            )
        #total_hours check
        total_hours = self.hours_lecture + self.hours_lab + self.practice_hours
        if total_hours == 0:
            raise ValidationError({
                'hours_lecture': _('Total course hours (lecture, lab, practice) must be greater than zero')
            })
        expected_min_hours=self.credits * 1 # 1 hour per credit at minimum
        if total_hours < expected_min_hours:
            raise ValidationError({
                'credits': _('Total course hours (lecture, lab, practice) must be greater than or equal to {} hours'.format(expected_min_hours))
            })
    def save(self, *args, **kwargs):
        # clean and save
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_total_hours(self):
        # return total hours
        return self.hours_lecture + self.hours_lab + self.practice_hours
    
    def get_learning_outcomes(self):
        # return a list of learning outcomes
        if not self.learning_outcomes:
            return []
        return [
            learning_outcome.strip() for learning_outcome in self.learning_outcomes.split('\n')if learning_outcome.strip()
        ]
    
    def get_all_prerequisites(self,include_indirect=False):
        # return a list of all prerequisites direct and indirect
        direct_prerequisites = self.prerequisites.filter(is_active=True)

        if not include_indirect:
            return direct_prerequisites
        
        #get indirect prerequisites recursively
        all_prerequisites = set(direct_prerequisites)
        for prerequisite in direct_prerequisites:
            all_prerequisites.update(prerequisite.get_all_prerequisites(include_indirect=True))

        return all_prerequisites

    def check_circular_prerequisites(self):
        # check for circular prerequisites
        visited=set()
        path=['self']

        def dfs(course):
            visited.add(course.id)
            for prerequisite in course.prerequisites.filter(is_active=True):
                if prerequisite.id ==self.id:
                    return True
                if prerequisite.id not in visited:
                    path.append(prerequisite)
                    if dfs(prerequisite):
                        return True
                    path.pop()
            return False
        # call dfs
        return dfs(self)

class Module(models.Model):
    course=models.ForeignKey(
        Course, on_delete=models.CASCADE, 
        related_name='modules',verbose_name=_("Course"), help_text=_("Course to which the module belongs"))
    title=models.CharField(
        max_length=255,
        verbose_name=_("Module Title"),
        help_text=_("Title of the module")
    )
    description=models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Module Description"),
        help_text=_("Description of the module")
    )
    order=OrderField(blank=True,for_fields=['course']
    )
    created_at=models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("When the module was created")
    )
    updated_at=models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("When the module was last updated")
    )
    photo=models.ImageField(
        blank=True,
        upload_to='Courses/Modules/photos/%Y/%m/%d/',
    )
    class Meta:
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")
        ordering = ['order']
        indexes = [
            models.Index(fields=['order'], name='module_order_idx'),
            models.Index(fields=['course'], name='module_course_idx'),
        ]
    
    def __str__(self):
        return f"{self.order} - {self.title}"
    

class Content(models.Model):
    module=models.ForeignKey(
        Module, on_delete=models.CASCADE, 
        related_name='contents',verbose_name=_("Module"), help_text=_("Module to which the content belongs"))
    content_type=models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content Type"),
    )    
    object_id=models.PositiveIntegerField()
    item=GenericForeignKey('content_type', 'object_id')
    order=OrderField(blank=True,for_fields=['module'])
    class Meta:
        verbose_name = _("Content")
        verbose_name_plural = _("Contents")
        ordering = ['order']
    
    def __str__(self):
        return f"{self.order} - {self.item}"


class ItemBase(models.Model):
    owner=models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='%(class)s_related',
    )
    title=models.CharField(
        max_length=250,
        verbose_name=_("Title"),
        help_text=_("Title of the item")
    )
    created_at=models.DateTimeField(
        auto_now_add=True,
    )
    updated_at=models.DateTimeField(
        auto_now=True,
    )
    class Meta:
        abstract=True
    
    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html', {'item':self})

    def __str__(self):
        return self.title
    
class Text(ItemBase):
    content = models.TextField()
    
    def is_text(self):
        return True

class File(ItemBase):
    file = models.FileField(upload_to='files')
    
    def is_file(self):
        return True


class Image(ItemBase):
    file = models.FileField(upload_to='images')

    def is_image(self):
        return True
    
class Video(ItemBase):
    url = models.URLField()

    def is_video(self):
        return True
# انشئ نموذج العلاقة بين الكورسات والبرامج الاكاديمية