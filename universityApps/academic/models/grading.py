"""Evaluations Models and Student Grading"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class GradeScale(models.Model):
    """Grading Scale Model"""
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description") , blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name=_("Default"))

    class Meta:
        verbose_name = _("Grading Scale")
        verbose_name_plural = _("Grading Scales")
        indexes = [
            models.Index(fields=['is_default'], name='grading_scale_is_default_idx'),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """ validate the grading scale data """
        if self.is_default:
            # make sure there is only one default scale
            default_scales=GradeScale.objects.filter(is_default=True)
            if self.id:
                default_scales = default_scales.exclude(id=self.id)
            if default_scales.exists():
                raise ValidationError({'is_default': _("Another scale is already set as default")})
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default(cls):
        """Get the default grading scale"""
        try:
            return cls.objects.get(is_default=True)
        except cls.DoesNotExist:
            return None


class Grade(models.Model):
    """Grade Model"""
    scale = models.ForeignKey(GradeScale, on_delete=models.PROTECT, verbose_name=_("Scale"), related_name='scale_grades')
    Letter =models.CharField(max_length=5, verbose_name=_("Letter"))
    description = models.TextField(verbose_name=_("Description"),max_length=100, )
    points = models.DecimalField(verbose_name=_("Points"), max_digits=3, decimal_places=2)
    min_percent = models.DecimalField(verbose_name=_("Min. Percentage"), max_digits=5, decimal_places=2)
    max_percent = models.DecimalField(verbose_name=_("Max. Percentage"), max_digits=5, decimal_places=2)
    is_passing = models.BooleanField(default=True, verbose_name=_("Passing"))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        verbose_name = _("Grade")
        verbose_name_plural = _("Grades")
        ordering = ['scale','-order']
        unique_together = ['scale', 'Letter']
        indexes = [
            models.Index(fields=['scale', 'Letter'], name='grade_scale_letter_idx'),
            models.Index(fields=['min_percent'], name='grade_min_percent_idx'),
            models.Index(fields=['max_percent'], name='grade_max_percent_idx'),
        ]

    def __str__(self):
        return f"{self.Letter} - {self.description}"

    def clean(self):
        """ validate the grade data """
        if self.min_percent and self.max_percent and self.min_percent > self.max_percent:
            raise ValidationError({'min_percent': _("Minimum percentage must be less than maximum percentage")})

        if self.min_percent and self.max_percent and self.min_percent < 0 or self.max_percent > 100:
            raise ValidationError({'min_percent': _("Minimum and maximum percentage must be between 0 and 100")})

        if self.min_percent and self.max_percent and self.min_percent == self.max_percent:
            raise ValidationError({'min_percent': _("Minimum and maximum percentage must be different")})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_grade_for_value(cls, numeric_value, scale=None):
        """Get the grade for a given numeric value """
        if scale is None:
            scale = GradeScale.get_default()
            if scale is None:
                return None
        
        try:
            return cls.objects.get(
                scale=scale,
                min_percent__lte=numeric_value,
                max_percent__gte=numeric_value,
            )
        except cls.DoesNotExist:
            return None

class GradeComponent(models.Model):
    """Grade Component Model"""
    class ComponentTypes(models.TextChoices):
        Quiz = 'Quiz', _('Quiz')
        Assignment = 'Assignment', _('Assignment')
        Project = 'Project', _('Project')
        Participation = 'Participation', _('Participation')
        Midterm = 'Midterm', _('Midterm Exam')
        Final = 'Final', _('Final Exam')
        Lab = 'Lab', _('Lab work')
        Presentation = 'Presentation', _('Presentation')
        Other = 'Other', _('Other')
    
    semester_course = models.ForeignKey('academic.SemesterCourse', on_delete=models.PROTECT, verbose_name=_("Semester Course"), related_name='grade_components')
    name = models.CharField(max_length=100, verbose_name=_("Component Name"))
    type = models.CharField(max_length=20, choices=ComponentTypes.choices, verbose_name=_("Component Type"))
    weight = models.DecimalField(verbose_name=_("Weight (%)"), max_digits=5, decimal_places=2)
    max_score = models.DecimalField(verbose_name=_("Maximum Score"), max_digits=5, decimal_places=2)
    due_date = models.DateField(verbose_name=_("Due Date"), blank=True, null=True)
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    is_required = models.BooleanField(default=True, verbose_name=_("Required"))

    class Meta:
        verbose_name = _("Grade Component")
        verbose_name_plural = _("Grade Components")
        ordering = ['semester_course', 'due_date']
        indexes = [
            models.Index(fields=['semester_course'], name='grade_component_course_idx'),
            models.Index(fields=['weight'], name='grade_component_weight_idx'),
        ]

    def __str__(self):
        return f"{self.semester_course} - {self.name} ({self.weight}%)"
    
    def clean(self):
        """ validate the grade component data """
        # make sure the weight is between 0 and 100
        total_weight = GradeComponent.objects.filter(
            semester_course=self.semester_course
        ).exclude(id=self.id).aaggregate(
            total=models.Sum('weight')
        )['total'] or 0

        if total_weight + self.weight > 100:
            raise ValidationError(
                {'weight': _("Total weight of all components cannot exceed 100%. Current total: %(total)s")},
                  params={'total':total_weight + self.weight
                })
        
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StudentGrade(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.PROTECT, verbose_name=_("Student"), related_name='grades')
    semester_course = models.ForeignKey('academic.SemesterCourse', on_delete=models.PROTECT, verbose_name=_("Semester Course"), related_name='grades_per_student')
    semester = models.ForeignKey('academic.Semester', on_delete=models.PROTECT, verbose_name=_("Semester"), related_name='semester_grades')
    grade=models.ForeignKey('academic.Grade', on_delete=models.PROTECT, verbose_name=_("Grade"), related_name='student_grades')
    numeric_value = models.DecimalField(verbose_name=_("Numeric Value"), max_digits=5, decimal_places=2)
    grade_points = models.DecimalField(verbose_name=_("Grade Points"), max_digits=3, decimal_places=2)
    is_included_in_gpa = models.BooleanField(default=True, verbose_name=_("Included in GPA"))
    graded_by = models.ForeignKey('users.FacultyMember', on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_grades', verbose_name=_("Graded By"))
    graded_date = models.DateField(verbose_name=_("Graded Date"), auto_now_add=True,db_index=True)
    last_modified = models.DateTimeField(verbose_name=_("Last Modified"), auto_now=True)
    notes = models.TextField(verbose_name=_("Notes"), blank=True, null=True)

    class Meta:
        verbose_name = _("Student Grade")
        verbose_name_plural = _("Student Grades")
        unique_together = ['student', 'semester_course', 'semester']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.semester_course.course.name} - {self.grade.letter}"
    
    def save(self, *args, **kwargs):
        self.grade_points = self.grade.points
        super().save(*args, **kwargs)

        self.student.upadate_cgpa()
    
    @classmethod
    def claculate_gpa(cls, student, semester=None):
        """ calculate the gpa of a student in a semester """
        grades_query = cls.objects.filter(
            student=student,
            is_included_in_gpa=True,
        )

        if semester:
            grades_query = grades_query.filter(semester=semester)

        total_points = 0
        total_credits = 0

        for grade in grades_query:
            credits = grade.semester_course.course.credits
            total_points += float(grade.grade_points) * credits
            total_credits += credits

        if total_credits == 0:
            return 0.00
        
        return round(total_points / total_credits, 2)
    

class ComponoentScore(models.Model):
    """ grade component score """
    student = models.ForeignKey('users.Student', on_delete=models.PROTECT, verbose_name=_("Student"), related_name='component_scores')
    component = models.ForeignKey('academic.GradeComponent', on_delete=models.PROTECT, verbose_name=_("Component"), related_name='component_scores')
    score = models.DecimalField(verbose_name=_("Score"), max_digits=5, decimal_places=2)
    precentage = models.DecimalField(verbose_name=_("Precentage"), max_digits=5, decimal_places=2)
    weighted_score = models.DecimalField(verbose_name=_("Weighted Score"), max_digits=5, decimal_places=2)
    submitted_date = models.DateField(verbose_name=_("Submitted Date"), auto_now_add=True,db_index=True)
    graded_by = models.ForeignKey('users.FacultyMember', on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_component_scores', verbose_name=_("Graded By"))
    graded_date = models.DateField(verbose_name=_("Graded Date"), auto_now_add=True,db_index=True)
    feedback = models.TextField(verbose_name=_("Feedback"), blank=True, null=True)

    class Meta:
        verbose_name = _("Component Score")
        verbose_name_plural = _("Component Scores")
        unique_together = ['student', 'component']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.component.name}: {self.score}/{self.component.max_score}"

    def save(self, *args, **kwargs):
        """calculate the precentage"""
        if self.component.max_score > 0:
            self.precentage = (self.score / self.component.max_score) * 100
        else:
            self.precentage = 0

        # calculate the weighted score
        self.weighted_score = (self.precentage / 100) * self.component.weight
        super().save(*args, **kwargs)

        self.calculate_course_grade()
    
    def calculate_course_grade(self):
        """ calculate the course grade """
        #get all component scores for the student in this course
        semester_course = self.component.semester_course
        components = ComponoentScore.objects.filter(semester_course=semester_course)

        total_weighted_score = 0
        total_weight = 0

        for component in components:
            try:
                score = ComponoentScore.objects.filter(
                    student=self.student,
                    component=component
                )

                total_weighted_score += score.weighted_score
                total_weight += component.component.weight
            except ComponoentScore.DoesNotExist:
                pass

        required_components = components.filter(is_required=True )
        scored_required = ComponoentScore.objects.filter(
            student=self.student,
            component__in=required_components
        ).count()

        if scored_required == required_components.count() and total_weight > 0:
             final_Score = total_weighted_score 

             grade = Grade.objects.get_grade_for_value(final_Score)

             if grade :
                 StudentGrade.objects.update_or_create(
                     student=self.student,
                     course=semester_course.course,
                     semester=semester_course.semesterplan.semestertype,
                     defaults={
                         'grade':grade,
                         'numeric_value':final_Score,
                         'graded_by':self.graded_by,
                         'grade_points':grade.points
                     }
                 )


class Exam(models.Model):
    course = models.ForeignKey('academic.SemesterCourse', on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    component = models.OneToOneField('academic.GradeComponent', on_delete=models.CASCADE, related_name='exam')
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    instructions = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"
        indexes = [
            models.Index(fields=['course'], name='exam_course_idx'),
            models.Index(fields=['scheduled_date'], name='exam_date_idx'),
        ]

    def __str__(self):
        return f"{self.title} ({self.course})"

class ExamSection(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Exam Section"
        verbose_name_plural = "Exam Sections"
        ordering = ['order']

    def __str__(self):
        return f"{self.exam.title} - Section {self.order}: {self.title}"

class ExamQuestion(models.Model):
    section = models.ForeignKey(ExamSection, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    is_mcq = models.BooleanField(default=False)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Exam Question"
        verbose_name_plural = "Exam Questions"
        ordering = ['order']

    def __str__(self):
        return f"{self.section.exam.title} - Q{self.order}"

class MCQChoice(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "MCQ Choice"
        verbose_name_plural = "MCQ Choices"

    def __str__(self):
        return f"{self.text} {'✅' if self.is_correct else ''}"

class StudentExamSubmission(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='exam_submissions')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Student Exam Submission"
        verbose_name_plural = "Student Exam Submissions"
        unique_together = ['student', 'exam']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam.title}"

class ExamAnswer(models.Model):
    submission = models.ForeignKey(StudentExamSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    selected_choice = models.ForeignKey(MCQChoice, null=True, blank=True, on_delete=models.SET_NULL)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Exam Answer"
        verbose_name_plural = "Exam Answers"
        unique_together = ['submission', 'question']

    def __str__(self):
        return f"{self.submission.student.user.get_full_name()} - Q{self.question.order}"

    def save(self, *args, **kwargs):
        # Auto-grade MCQ
        if self.question.is_mcq and self.selected_choice:
            self.score = self.question.max_score if self.selected_choice.is_correct else 0
        super().save(*args, **kwargs)
