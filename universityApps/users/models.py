from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager,Group
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
from django.conf import settings
from django.db.models import Sum
from django.core.mail import send_mail
import uuid
from django.apps import apps
from .utils import (
     student_document_upload_path
)
class UserManager(BaseUserManager):
    #Custom user manager
    # use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra_fields):
        """ Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
    
class Roles(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    STAFF = 'staff', _('Staff Member')
    FACULTY = 'faculty', _('Faculty Member')
    STUDENT = 'student', _('Student')


class User(AbstractUser):
    """
    Default custom user model for universityApps.
    """
    class GENDER_CHOICES(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )

    role=models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.ADMIN,
        verbose_name=_("Role"),
        help_text=_("Role of the user")
    )
    uuid=models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        verbose_name=_("UUID"),
        help_text=_("Unique identifier for the user")
    )
    email=models.EmailField(
        unique=True,
        verbose_name=_("Email"),
        help_text=_("Email address of the user")
    )
    username = models.CharField(
        _('Username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        validators=[MinLengthValidator(3)],
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    #Additional personal information
    national_id = models.CharField(
        _('National ID'),
        max_length=20,
        blank=True,
        null=True,
        unique=True
    )
    nationality = models.CharField(_('Nationality'), max_length=100, blank=True, null=True)
    secondary_email = models.EmailField(_('Secondary Email'), blank=True, null=True)
    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(
        _('Phone Number'),
        validators=[phone_regex],
        max_length=17,
        unique=True,
        error_messages={
            'unique': _("A user with that phone number already exists," \
            "your phone number must be unique"),
        }
    )
    #Birth information
    date_of_birth = models.DateField(_('Date of Birth'), blank=True, null=True)

    #Address information
    address = models.TextField(_('Address'), blank=True, null=True)
    city = models.CharField(_('City'), max_length=100, blank=True, null=True)
    state = models.CharField(_('State/Province'), max_length=100, blank=True, null=True)
    country = models.CharField(_('Country'), max_length=100, blank=True, null=True)

    # Additional information for system 
    is_active = models.BooleanField(_('Active'), default=True)
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)

    #Relations with other applications
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_users',
        verbose_name=_('Department')
    )
    
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='college_users',
        verbose_name=_('College')
    )
    #Set email as login identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name']

    # set custom user manager
    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering =[ 'first_name','last_name']
   
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name.strip()
    
    def email_user(self, subject, message, from_email = None, **kwargs):
        """ Send an email to this user."""
        send_mail(subject, message, from_email, **kwargs)
    
    def assign_group_by_role(self):
        if self.role:
            group,created = Group.objects.get_or_create(name=self.role)
            self.groups.clear()
            self.groups.add(group)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.assign_group_by_role()

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_("User"))
#     profile_picture = models.ImageField(upload_to='Users/Profile_Pics/%Y/%m/', blank=True, null=True)
#     bio = models.TextField(verbose_name=_("Biography"),blank=True, null=True)
#     website = models.URLField(blank=True, null=True)
#     social_media_links = models.JSONField(default=dict, verbose_name=_("Social Media Links"), blank=True, null=True)
#     timezone = models.CharField(max_length=50, verbose_name=_("Timezone"), blank=True, null=True)
#     avater =models.ImageField(upload_to='Users/Avatars/%Y/%m/', blank=True, null=True)

#     class Meta:
#         verbose_name = _("User Profile")
#         verbose_name_plural = _("User Profiles")
    
#     def __str__(self):
#         return f"{self.user.get_full_name()}'s Profile"

class Student(models.Model):
    class StudentStatus(models.TextChoices):
        ACTIVE = 'active', _('Active')
        GRADUTATED = 'graduated', _('Graduated')
        SUSPENDED = 'suspended', _('Suspended')
        Dismissed = 'dismissed', _('Dismissed')
    #User Account
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student', verbose_name=_("User"))
    # Student Information
    student_id = models.CharField(max_length=20, verbose_name=_("Student ID"), unique=True)
    admission_date = models.DateField(verbose_name=_("Admission Date"), default=timezone.now,db_index=True)
    status= models.CharField(max_length=20, verbose_name=_("Status"), choices=StudentStatus.choices, default=StudentStatus.ACTIVE)
    secondary_phone_number = models.CharField(max_length=20, verbose_name=_("Secondary Phone Number"), blank=True, null=True)


    place_of_birth= models.CharField(max_length=100, verbose_name=_("Place of Birth"), blank=True, null=True)
    direcorate= models.CharField(max_length=100, verbose_name=_("Directorate"), blank=True, null=True)
    #qualification information
    previous_qualifications = models.TextField(verbose_name=_("Previous Qualifications"), blank=True, null=True)
    qualification_average  = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Qualification Average"), blank=True, null=True)
    qualification_institution  = models.CharField(max_length=100, verbose_name=_("Where To Get the Qualification"), blank=True, null=True)
    date_obtained = models.DateField(verbose_name=_("Date Obtained"), blank=True, null=True)

    #academic information
    program = models.ForeignKey('programs.AcademicProgram',on_delete=models.SET_NULL,null=True,blank=True,related_name='program_students',verbose_name=_('Program'))
    department = models.ForeignKey('departments.Department',on_delete=models.SET_NULL,null=True,blank=True,related_name='department_students',verbose_name=_('Department'))

    cgpa=models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("CGPA"), default=0.00,db_index=True)
    total_credits_earned = models.PositiveSmallIntegerField(verbose_name=_("Total Credits Earned"),default=0,)
    #Emergency Contact Information
    emergency_contact_name = models.CharField(_('Emergency Contact Name'),max_length=100,blank=True,null=True)
    emergency_contact_phone = models.CharField(_('Emergency Contact Phone'),max_length=17,blank=True,null=True)
    emergency_contact_relationship = models.CharField(_('Emergency Contact Relationship'),max_length=50,blank=True,null=True)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
        ordering = ['student_id',]
        indexes = [
            models.Index(fields=['student_id'], name='student_student_id_idx'),
            models.Index(fields=['status'], name='student_status_idx'),
        ]
    def __str__(self):
        return f"{self.user.get_full_name()}'s {self.student_id}"
    
    def upadate_cgpa(self):
        """ update cgpa of student """
        StudentsGrade=apps.get_model('universityApps.academic', 'StudentsGrade')
        #get all the student's grades
        grades=StudentsGrade.objects.filter(
            student=self,
            grade__isnull=False
        )

        if not grades.exists():
            return  0.00
        
        total_points=0
        total_credits=0
        for grade in grades:
            total_points += grade.grade*grade.course.credits
            total_credits += grade.course.credits
        
        if total_credits >0:
            gpa=total_points/total_credits
            precentage= (gpa / 4.0) * 100 
            self.cgpa=round(precentage,2)
        else:
            self.cgpa=0.00

        self.save(update_fields=['cgpa'])
        return self.cgpa
    
    def update_credits_earned(self):
        """ update total credits earned by student """
        StudentsGrade=models.get_model('universityApps.academic', 'StudentsGrade')
        credits=StudentsGrade.objects.filter(
            student=self,
            grade__is__passing=True
        ).aggregate(
            total_credits=Sum('course__credits')
        )['total_credits'] or 0

        self.total_credits_earned=credits
        self.save(update_fields=['total_credits_earned'])
        return self.total_credits_earned

class StudentDocument(models.Model):
    class DocumentType(models.TextChoices):
        NATIONAL_ID = 'national_id', _("National ID")
        HIGH_SCHOOL = 'high_school', _("High School Certificate")
        PERSONAL_PHOTO = 'photo', _("Personal Photo")
        OTHER = 'other', _("Other")

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("Student")
    )
    document_type = models.CharField(max_length=50, choices=DocumentType.choices, verbose_name=_("Document Type"))
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Document Title"))
    file = models.FileField(upload_to=student_document_upload_path, verbose_name=_("File"))
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.student.user.get_full_name()}"


class FacultyMember(models.Model):
    class FACULTY_STATUS(models.TextChoices):
        ACTIVE = 'active', _('Active')
        ON_LEAVE = 'on_leave', _('On Leave')
        SABBATICAL = 'sabbatical', _('Sabbatical')
        RETIRED = 'retired', _('Retired')
        TERMINATED = 'terminated', _('Terminated')

    class FACULTY_RANK(models.TextChoices):
        PROFESSOR = 'professor', _('Professor')
        ASSOCIATE_PROFESSOR = 'associate_professor', _('Associate Professor')
        ASSISTANT_PROFESSOR = 'assistant_professor', _('Assistant Professor')
        LECTURER = 'lecturer', _('Lecturer')
        INSTRUCTOR = 'instructor', _('Instructor')
        ADJUNCT = 'adjunct', _('Adjunct Faculty')
        VISITING = 'visiting', _('Visiting Faculty')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='faculty',
        verbose_name=_("User"),
        help_text=_("User to which the faculty member belongs")
    )
    Faculty_id=models.CharField(max_length=30, verbose_name=_("Faculty ID"), unique=True)
    hire_date = models.DateField(verbose_name=_("Hire Date"), default=timezone.now)
    status = models.CharField(
        max_length=30,
        choices=FACULTY_STATUS.choices,
        default=FACULTY_STATUS.ACTIVE,
        verbose_name=_("Status"),
        help_text=_("Status of the faculty member")
    )
    rank = models.CharField(
        max_length=30,
        choices=FACULTY_RANK.choices,
        default=FACULTY_RANK.INSTRUCTOR,
        verbose_name=_("Rank"),
        help_text=_("Rank of the faculty member")
    )

    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faculty_members',
        verbose_name=_('Department')
    )
    specialization = models.CharField(
        _('Specialization'),
        max_length=200,
        blank=True,
        null=True
    )
    
    research_interests = models.TextField(
        _('Research Interests'),
        blank=True,
        null=True
    )
    
    publications = models.TextField(
        _('Publications'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Faculty Member")
        verbose_name_plural = _("Faculty Members")
        ordering = ['Faculty_id',]
        indexes = [
            models.Index(fields=['Faculty_id'], name='faculty_Faculty_id_idx'),
            models.Index(fields=['status'], name='faculty_status_idx'),
        ]
    
    def __str__(self):
        return f"{self.get_rank_display()} {self.user.get_full_name()}'s {self.Faculty_id}"
    
    def is_department_head(self):
        """ Check if the faculty member is the department head """
        if not self.department:
            return False
        return self.department.head == self
    
    def is_college_dean(self):
        """ Check if the faculty member is the college dean """
        if not self.department or not self.department.college:
            return False
        return self.department.college.dean == self


class StaffMember(models.Model):
    class stauff_status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        ON_LEAVE = 'on_leave', _('On Leave')
        Terminated = 'terminated', _('Terminated')
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_("User"),
        help_text=_("User to which the staff member belongs")
    )
    stuff_id=models.CharField(max_length=30, verbose_name=_("Stuff ID"), unique=True)
    hire_date = models.DateField(verbose_name=_("Hire Date"), default=timezone.now)
    status=models.CharField(
        verbose_name=_("Status"),
        choices=stauff_status.choices,
        default=stauff_status.ACTIVE,
        max_length=30,
        help_text=_("Status of the staff member")
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members',
        verbose_name=_('Department')
    )
    job_title = models.CharField(
        _('Job Title'),
        max_length=200,
        blank=True,
        null=True
    )
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_supervisor',
        verbose_name=_('Supervisor')
    )    
    class Meta:
        verbose_name = _("Staff Member")
        verbose_name_plural = _("Staff Members")
        ordering = ['stuff_id']
        indexes = [
            models.Index(fields=['stuff_id'], name='staff_stuff_id_idx'),
            models.Index(fields=['status'], name='staff_status_idx'),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s {self.stuff_id}"

class UserLog(models.Model):
    """Model to log user login and logout times"""
    class LogType(models.TextChoices):
        LOGIN = 'login', _('Login')
        LOGOUT = 'logout', _('Logout')
        PASSWORD_CHANGE = 'password_change', _('Password Change')
        PROFILE_UPDATE = 'profile_update', _('Profile Update')
        ROLE_CHANGE = 'role_change', _('Role Change')
        SATUS_CHANGE = 'status_change', _('Status Change')
        OTHER = 'other', _('Other')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"), help_text=_("User who logged in"),related_name='logs')
    logtype=models.CharField(max_length=30, verbose_name=_("Log Type"), choices=LogType.choices, default=LogType.OTHER)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"), help_text=_("Time of the log"))
    user_agent=models.TextField(verbose_name=_("User Agent"), help_text=_("User agent of the user") ,blank=True, null=True)
    details=models.JSONField(verbose_name=_("Details"), help_text=_("Details of the log"), blank=True, null=True)

    class Meta:
        verbose_name = _("User Log")
        verbose_name_plural = _("User Logs")
        ordering = ['-timestamp',]

    def __str__(self):
        return f"{self.user.get_full_name()}'s {self.get_logtype_display()} at {self.timestamp}"

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        System = 'system', _('System')
        Academic = 'academic', _('Academic')
        Enrollement = 'enrollement', _('Enrollement')
        Grade='grade', _('Grade')
        Announcement='announcement', _('Announcement')
        Message='message', _('Message')
        Other = 'other', _('Other')
    class NotificationPriority(models.TextChoices):
        High = 'high', _('High')
        Medium = 'medium', _('Medium')
        Low = 'low', _('Low')  
        Urgent = 'urgent', _('Urgent')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"), help_text=_("User to which the notification belongs"),related_name='notifications')
    title=models.CharField(max_length=200, verbose_name=_("Title"), help_text=_("Title of the notification"))
    message=models.TextField(verbose_name=_("Message"), help_text=_("Message of the notification"))
    notification_type=models.CharField(max_length=30, verbose_name=_("Type"), choices=NotificationType.choices, default=NotificationType.Other)
    priority=models.CharField(max_length=30, verbose_name=_("Priority"), choices=NotificationPriority.choices, default=NotificationPriority.Medium)
    created_at=models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"), help_text=_("Time when the notification was created"))
    read = models.BooleanField(default=False, verbose_name=_("Read"), help_text=_("Whether the notification has been read"))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Read At"), help_text=_("Time when the notification was read"))
    link = models.URLField(max_length=200, verbose_name=_("Link"), help_text=_("Link to the notification"), blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Sender"), help_text=_("User who sent the notification"),related_name='sent_notifications')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"), help_text=_("Time of the notification"))

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at',]

    def __str__(self):
        return f"{self.user.get_full_name()}'s {self.title}"
    
    def mark_as_read(self):
        """ Mark the notification as read """
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save( update_fields=['read', 'read_at'])
            return True
        return False
    
    def mark_as_unread(self):
        """ Mark the notification as unread """
        if self.read:
            self.read = False
            self.read_at = None
            self.save( update_fields=['read', 'read_at'])
            return True
        return False