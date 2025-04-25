from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum

class StudentEnrollment(models.Model):
    class EnrollmentStatus(models.TextChoices):
        ACTIVE = 'active', _('Active')
        GRADUTATED = 'graduated', _('Graduated')
        SUSPENDED = 'suspended', _('Suspended')
        Dismissed = 'dismissed', _('Dismissed')
        WITHDRAWN = 'withdrawn', _('Withdrawn')

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE)
    program = models.ForeignKey('programs.AcademicProgram', on_delete=models.CASCADE)
    study_plan = models.ForeignKey('academic.StudyPlan', on_delete=models.PROTECT)
    enrollment_date = models.DateField(verbose_name=_("Enrollment Date"), default=timezone.now,db_index=True)
    status = models.CharField(max_length=10, choices=EnrollmentStatus.choices, default=EnrollmentStatus.ACTIVE)
    actual_graduation_date = models.DateField(verbose_name=_("Actual Graduation Date"), blank=True, null=True)
    notes = models.TextField(verbose_name=_("Notes"), blank=True, null=True)

    class Meta:
        unique_together = ['student', 'program', 'study_plan']
        verbose_name = _("Student Enrollment")
        verbose_name_plural = _("Student Enrollments")

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.program.name}"
    
    def clean(self):
        if self.status == StudentEnrollment.EnrollmentStatus.ACTIVE:
            if StudentEnrollment.objects.filter(student=self.student, status=StudentEnrollment.EnrollmentStatus.ACTIVE).exclude(id=self.id).exists():
                raise ValidationError("Only one active enrollment is allowed for a student.")
    
    def activate(self):
        if self.status != StudentEnrollment.EnrollmentStatus.ACTIVE:
            self.status = StudentEnrollment.EnrollmentStatus.ACTIVE
            self.save()
            return True
        return False
    
    def put_on_hold(self , reason):
        if self.status == StudentEnrollment.EnrollmentStatus.ACTIVE:
            self.status = StudentEnrollment.EnrollmentStatus.SUSPENDED
            if reason:
                self.notes = f"{self.notes}\n[{timezone.now().date()}] On Hold: {reason}"
            self.save()
            return True
        return False
    
    def dismiss(self , reason):
        if self.status == StudentEnrollment.EnrollmentStatus.ACTIVE or self.status == StudentEnrollment.EnrollmentStatus.SUSPENDED:
            self.status = StudentEnrollment.EnrollmentStatus.Dismissed
            if reason:
                self.notes = f"{self.notes}\n[{timezone.now().date()}] Dismissed: {reason}"
            self.save()
            return True
        return False
    
    def withdraw(self , reason):
        if self.status == StudentEnrollment.EnrollmentStatus.ACTIVE or self.status == StudentEnrollment.EnrollmentStatus.SUSPENDED:
            self.status = StudentEnrollment.EnrollmentStatus.WITHDRAWN
            if reason:
                self.notes = f"{self.notes}\n[{timezone.now().date()}] Withdrawn: {reason}"
            self.save()
            return True
        return False
    
    def graduate(self ):
        if self.status == StudentEnrollment.EnrollmentStatus.ACTIVE:
            self.status = StudentEnrollment.EnrollmentStatus.GRADUTATED
            self.save()
            return True
        return False
    
    def change_study_plan(self, new_study_plan, reason=None):
        old_plan = self.study_plan
        self.study_plan = new_study_plan
        if reason:
            self.notes = f"{self.notes}\n[{timezone.now().date()}] Study Plan Changed from {old_plan} to {new_study_plan}: {reason}"
        self.save()
        return True
    

class SemesterRegistration(models.Model):
    class RegistrationStatus(models.TextChoices):
        Draft = 'draft', _('Draft')
        Pending = 'pending', _('Pending')
        Approved = 'approved', _('Approved')
        Rejected = 'rejected', _('Rejected')
        Active = 'active', _('Active')
        Completed = 'completed', _('Completed')
        Withdrawn = 'withdrawn', _('Withdrawn')

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE , related_name='student_semester_registrations', verbose_name=_("Student"))
    semester = models.ForeignKey('academic.Semester', on_delete=models.PROTECT, related_name='semester_registrations', verbose_name=_("Semester"))
    academic_year = models.ForeignKey('academic.AcademicYear', on_delete=models.PROTECT, related_name='academic_year_semester_registrations', verbose_name=_("Academic Year"))
    registration_date = models.DateTimeField(verbose_name=_("Registration Date"), default=timezone.now,db_index=True)
    status = models.CharField(max_length=10, choices=RegistrationStatus.choices, default=RegistrationStatus.Draft)
    approved_by = models.ForeignKey('users.FacultyMember', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_registrations', verbose_name=_("Approved By"))
    approval_date = models.DateTimeField(verbose_name=_("Approval Date"), blank=True, null=True)
    total_credits = models.PositiveIntegerField(verbose_name=_("Total Credits"), default=0)
    notes = models.TextField(verbose_name=_("Notes"), blank=True, null=True)

    class Meta:
        unique_together = ['student', 'semester', 'academic_year']
        verbose_name = _("Semester Registration")
        verbose_name_plural = _("Semester Registrations")
        indexes = [
            models.Index(fields=['academic_year'], name='semester_reg_year_idx'),
            models.Index(fields=['semester'], name='semester_reg_semester_idx'),
            models.Index(fields=['student'], name='semester_reg_student_idx'),
        ]

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.academic_year} - {self.semester.semester_type} " 
    
    def submit(self):
        """ Submit the registration for approval """
        if self.status == SemesterRegistration.RegistrationStatus.Draft:
            self.status = SemesterRegistration.RegistrationStatus.Pending
            self.save()
            return True
        return False
    
    def approve(self , approved_by):
        """ Approve the registration """
        if self.status == SemesterRegistration.RegistrationStatus.Pending:
            self.status = SemesterRegistration.RegistrationStatus.Approved
            self.approved_by = approved_by
            self.approval_date = timezone.now()
            self.save()
            return True
        return False
    
    def reject(self , reason):
        """ Reject the registration """
        if self.status == SemesterRegistration.RegistrationStatus.Pending:
            self.status = SemesterRegistration.RegistrationStatus.Rejected
            if reason:
                self.notes = f"{self.notes}\n[{timezone.now().date()}] Rejected: {reason}"
            self.save()
            return True
        return False
    
    def activate(self):
        """ Activate the registration (beginning of the semester) """
        if self.status == SemesterRegistration.RegistrationStatus.Approved:
            self.status = SemesterRegistration.RegistrationStatus.Active
            self.save()
            return True
        return False
    
    def complete(self):
        """ Complete the registration (end of the semester) """
        if self.status == SemesterRegistration.RegistrationStatus.Active:
            self.status = SemesterRegistration.RegistrationStatus.Completed
            self.save()
            return True
        return False
    
    def withdraw(self):
        """student withdraws from the semester"""
        if self.status == SemesterRegistration.RegistrationStatus.Active or self.status == SemesterRegistration.RegistrationStatus.Pending:
            self.status = SemesterRegistration.RegistrationStatus.Withdrawn
            self.save()
            return True
        return False
    
    def calculate_total_credits(self):
        """ Calculate the total credits for the registration """
        total=self.course_registrations.filter(
            status__in=[
                CourseRegistration.RegistrationStatus.Registered,
                CourseRegistration.RegistrationStatus.completed
            ]
        ).aggregate(total=models.Sum('semester_course__course__credits'))['total'] or 0
        self.total_credits = total
        self.save(update_fields=['total_credits'])
        return total
    
    def validate_registration(self):
        """ Validate the registration """
        
        self.calculate_total_credits()
        program_settings=self.student.program.programsettings

        min_credits=program_settings.min_credits_per_semester
        max_credits=program_settings.max_credits_per_semester

        if self.total_credits < min_credits:
            raise ValidationError(
                {'total_credits':_("Total credits %(total)s are below the minimum required %(min)s")},
                params={ 'total':self.total_credits,'min':min_credits}
            )
        
        if self.total_credits > max_credits:
            raise ValidationError(
                {'total_credits':_("Total credits %(total)s are above the maximum allowed %(max)s")}, 
                params={ 'total':self.total_credits,'max':max_credits}
            )
        
        return True
    


class CourseRegistration(models.Model):
    class RegistrationStatus(models.TextChoices):
        Registered = 'registered', _('Registered')
        dropped = 'dropped', _('Dropped')
        withdrawn = 'withdrawn', _('Withdrawn')
        completed = 'completed', _('Completed')
        failed = 'failed', _('Failed')
        incomplete = 'incomplete', _('Incomplete')
    
    semester_registration = models.ForeignKey(
        'academic.SemesterRegistration', 
        on_delete=models.CASCADE, 
        related_name='course_registrations', 
        verbose_name=_("Semester Registration")
        )
    semester_course = models.ForeignKey(
        'academic.SemesterCourse', 
        on_delete=models.PROTECT, 
        related_name='semester_course_registrations', 
        verbose_name=_("Semester Course")
        )
    registration_date = models.DateField(verbose_name=_("Registration Date"), default=timezone.now,db_index=True)
    status = models.CharField(max_length=10, choices=RegistrationStatus.choices, default=RegistrationStatus.Registered)
    grade = models.ForeignKey(
        'academic.StudentGrade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grade_course_registrations',
        verbose_name=_("Grade")
    )
    is_repeat = models.BooleanField(default=False, verbose_name=_("Is Repeat"))

    notes = models.TextField(null=True, blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Course Registration")
        verbose_name_plural = _("Course Registrations")
        unique_together = ['semester_registration', 'semester_course']
        indexes = [
            models.Index(fields=['semester_registration'], name='c_registration_semester_idx'),
            models.Index(fields=['status'], name='course_registration_status_idx'),
            models.Index(fields=['is_repeat'], name='registration_is_repeat_idx'),
            models.Index(fields=['semester_course'], name='semester_registration_idx'),
        ]
    def __str__(self):
        return f"{self.semester_registration.student.user.get_full_name()} - {self.semester_course.course.name}"
    
    def drop(self, reason=None):
        """drop the course (during add/drop period)"""
        if self.status == CourseRegistration.RegistrationStatus.Registered and self.semester_registration.semester.is_add_drop_period():
            self.status = CourseRegistration.RegistrationStatus.dropped
            if reason:
                self.notes = f"{self.notes}\n[{timezone.now().date()}] Dropped: {reason}"
            self.save()
            self.semester_registration.calculate_total_credits()
            return True
        return False
    
    def withdraw(self, reason=None):
        """student withdraws from the course (after add/drop period)"""
        if self.status == CourseRegistration.RegistrationStatus.Registered and not self.semester_registration.semester.is_withdrawal_allowed():
            self.status = CourseRegistration.RegistrationStatus.withdrawn
            if reason:
                self.notes = f"{self.notes}\n[{timezone.now().date()}] Withdrawn: {reason}"
            self.save()
            return True
        return False
    
    def complete(self, grade_value=None):
        """successfully complete the course """
        if self.status == CourseRegistration.RegistrationStatus.Registered:
            self.status = CourseRegistration.RegistrationStatus.completed
            
            # if grade is assigned ,create grade record for the student
            if grade_value is not None:
                from universityApps.academic.models import StudentGrade, Grade 

                #Find the suitable grade
                grade=Grade.objects.get_grade_for_value(grade_value)


                #create student grade record
                student_grade = StudentGrade.objects.create(
                    student=self.semester_registration.student,
                    course=self.semester_course.course,
                    grade=grade,
                    numeric_value=grade_value,
                    semester=self.semester_registration.semester,
                )
                self.grade = student_grade

            self.save()
            return True
        return False
    
    def fail(self, grade_value=None):
        """student fails the course"""
        if self.status == CourseRegistration.RegistrationStatus.Registered:
            self.status = CourseRegistration.RegistrationStatus.failed

            # if grade is assigned ,create grade record for the student
            if grade_value is not None:
                from universityApps.academic.models import StudentGrade, Grade 

                #Find the suitable grade
                grade=Grade.objects.get_grade_for_value(grade_value)

                #create student grade record
                student_grade = StudentGrade.objects.create(
                    student=self.semester_registration.student,
                    course=self.semester_course.course,
                    grade=grade,
                    numeric_value=grade_value,
                    semester=self.semester_registration.semester,
                )
                self.grade = student_grade

            self.save()
            return True
        return False
    
    def mark_incomplete(self, reason=None):
        """mark the course as incomplete"""
        if self.status == CourseRegistration.RegistrationStatus.Registered:
            self.status = CourseRegistration.RegistrationStatus.incomplete
            if reason:
                self.notes = f"{self.notes}\n[{timezone.now().date()}] Incomplete: {reason}"
            self.save()
            return True
        return False
    

class StudentGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    semester = models.ForeignKey('academic.Semester', on_delete=models.CASCADE, verbose_name=_("Semester"))
    program = models.ForeignKey('programs.AcademicProgram', on_delete=models.CASCADE, verbose_name=_("Program"))
    level = models.ForeignKey('programs.AcademicLevel', on_delete=models.CASCADE, verbose_name=_("Level"))
    max_students = models.PositiveSmallIntegerField(verbose_name=_("Max Students"), default=25)

    class Meta:
        verbose_name = _("Student Group")
        verbose_name_plural = _("Student Groups")
        ordering = ['name']

    def __str__(self):
        return f"{self.level.name} {self.program.department.name} {self.name}"
    
    def current_size(self):
        return self.members.count()
    
    def is_full(self):
        return self.current_size() >= self.max_students
    

class StudentGroupMembership(models.Model):
    group = models.ForeignKey('academic.StudentGroup', on_delete=models.CASCADE, verbose_name=_("Group") , related_name='members')
    student = models.OneToOneField('users.Student', on_delete=models.CASCADE, verbose_name=_("Student") , related_name='group')



class GroupSchedule(models.Model):
    class Weekday(models.TextChoices):
        SUNDAY = 'sunday', _('Sunday')
        MONDAY = 'monday', _('Monday')
        TUESDAY = 'tuesday', _('Tuesday')
        WEDNESDAY = 'wednesday', _('Wednesday')
        THURSDAY = 'thursday', _('Thursday')
        FRIDAY = 'friday', _('Friday')
        SATURDAY = 'saturday', _('Saturday')

    group = models.ForeignKey('academic.StudentGroup', on_delete=models.CASCADE, related_name='schedules', verbose_name=_("Group"))
    semester_course = models.ForeignKey('academic.SemesterCourse', on_delete=models.CASCADE, related_name='group_schedules', verbose_name=_("Semester Course"))
    instructor = models.ForeignKey('users.FacultyMember', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Instructor"))
    classroom = models.ForeignKey('academic.Classroom', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Classroom"))

    day = models.CharField(max_length=10, choices=Weekday.choices, verbose_name=_("Day"))
    start_time = models.TimeField(verbose_name=_("Start Time"))
    end_time = models.TimeField(verbose_name=_("End Time"))
    is_online = models.BooleanField(default=False, verbose_name=_("Online Session"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Group Schedule")
        verbose_name_plural = _("Group Schedules")
        unique_together = ['group', 'semester_course', 'day', 'start_time']
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.group.name} | {self.semester_course.course.code} | {self.day} {self.start_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_("Start time must be before end time."))

    def is_now_live(self):
        now = timezone.now().time()
        today = timezone.now().strftime("%A").lower()
        return self.day == today and self.start_time <= now <= self.end_time
