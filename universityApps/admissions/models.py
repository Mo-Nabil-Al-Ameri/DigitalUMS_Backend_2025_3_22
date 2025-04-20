from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .utils import (
    send_acceptance_email, 
    generate_student_id,
    application_document_upload_path,
    send_rejection_email,
    )

User = get_user_model()

class AdmissionApplication(models.Model):
    """Program Admission Application Model"""
    class SatusChoices(models.TextChoices):
        SUBMITTED = 'submitted', _('Submitted')
        UNDER_REVIEW = 'under_review', _('Under Review')
        ACCEPTED = 'accepted', _('Accepted')
        REJECTED = 'rejected', _('Rejected')
        ADDITIONAL_INFO = 'additional_info', _('Additional Info Required')
        ACHIEVED = 'achieved', _('Achieved')
    # User information
    first_name = models.CharField(max_length=100, verbose_name=_("First Name") , help_text=_("Applicant\'s first name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"), help_text=_("Applicant\'s last name"))
    email = models.EmailField(verbose_name=_("Email"), help_text=_("Applicant\'s email address"),)
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), help_text=_("Applicant\'s phone number"), )
    birth_date = models.DateField(verbose_name=_("Birth Date"), help_text=_("Applicant\'s birth date"))
    national_id = models.CharField(max_length=30, verbose_name=_("National ID"), help_text=_("Applicant\'s national ID number"))
    # Student information
    previous_qualifications = models.TextField(verbose_name=_("Previous Qualifications"), blank=True, null=True)
    qualification_average  = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Qualification Average"), blank=True, null=True)
    qualification_institution  = models.CharField(max_length=100, verbose_name=_("Where To Get the Qualification"), blank=True, null=True)
    date_obtained = models.DateField(verbose_name=_("Date Obtained"), blank=True, null=True)
    program = models.ForeignKey('programs.AcademicProgram',on_delete=models.CASCADE,related_name='admission_applications',verbose_name=_('Program'))

    #Application Information
    status = models.CharField(max_length=20, choices=SatusChoices.choices, verbose_name=_("Status"))
    submission_date = models.DateTimeField(auto_now_add=True)

    reviewed_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')

    notes = models.TextField(null=True, blank=True)
    archived = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Admission Application")
        verbose_name_plural = _("Admission Applications")
        ordering = ['-submission_date']
        unique_together = ('email', 'phone_number','national_id','program')
        indexes = [
            models.Index(fields=['status'], name='application_status_idx'),
            models.Index(fields=['program'], name='application_program_idx'),
            models.Index(fields=['archived'], name='application_archived_idx'),
            models.Index(fields=['reviewed_by'], name='application_reviewed_by_idx'),
        ]

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name()} - {self.program}"
    
    def generate_username(self):
        base=self.full_name().lower().replace(' ','')
        shor_code= self.program.department.dept_no[2:]
        return f"{base[:7]}{int(timezone.now().timestamp()) % 10000}"
    
    def start_review(self, reviewed_by):
        """Starts the application review process"""
        if self.status == self.SatusChoices.SUBMITTED:
            self.status = self.SatusChoices.UNDER_REVIEW
            self.reviewed_by = reviewed_by
            self.reviewed_date = timezone.now()
            self.save(update_fields=['status', 'reviewed_by', 'reviewed_date'])
            return True
        return False
    
    def request_additional_info(self):
        """ Request additional information """
        if self.status in[ self.SatusChoices.UNDER_REVIEW, self.SatusChoices.SUBMITTED]:
            self.status = self.SatusChoices.ADDITIONAL_INFO
            self.save(update_fields=['status'])
            return True
        return False
    
    def accept(self,reviewed_by=None):
        from users.models import Student,StudentDocument,Roles
        username=self.generate_username()
        password=self.national_id

        # Create user
        user = User.objects.create_user(
            username=username,
            email=self.email,
            password=password,
            first_name=self.first_name,
            last_name=self.last_name,
            role=Roles.STUDENT,
            national_id=self.national_id,
            phone_number=self.phone_number,
            date_of_birth=self.birth_date,
        )
        student_id = generate_student_id( self.program )
        # Create student
        student = Student.objects.create(
            user=user,
            student_id=student_id,
            program=self.program,
            department=self.program.department,
            previous_qualifications=self.previous_qualifications,
            qualification_average=self.qualification_average,
            qualification_institution=self.qualification_institution,
            date_obtained=self.date_obtained,
            admission_date=timezone.now().date(),
        )

        # Create documents
        for document in self.application_documents.all():
            StudentDocument.objects.create(
                student=student,
                document_type=document.document_type,
                title=document.title,
                file=document.file,
            )

        self.status = self.SatusChoices.ACCEPTED
        self.reviewed_by = reviewed_by
        self.reviewed_date = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_date'])
        send_acceptance_email(self.email, self.full_name, self.program.name, username)

    def reject(self , reviewed_by=None, reason=None):
        """ Rejects the application """

        self.status = self.SatusChoices.REJECTED
        self.reviewed_by = reviewed_by
        self.reviewed_date = timezone.now()
        if reason:
            self.notes = f"{self.notes}\n {reason}"
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_date', 'notes'])

        send_rejection_email(self.email, self.full_name, self.program.name, reason)

    def get_status_color(self):
        return {
            self.SatusChoices.SUBMITTED: 'Secondary',
            self.SatusChoices.UNDER_REVIEW: 'Warning',
            self.SatusChoices.ACCEPTED: 'Success',
            self.SatusChoices.REJECTED: 'Danger',
            self.SatusChoices.ADDITIONAL_INFO: 'Info',
            self.SatusChoices.ACHIEVED: 'Muted',
        }.get(self.status, 'dark')
    
class ApplicationDocument(models.Model):
    class DocumentType(models.TextChoices):
        NATIONAL_ID = 'national_id', _("National ID")
        HIGH_SCHOOL = 'high_school', _("High School Certificate")
        PERSONAL_PHOTO = 'photo', _("Personal Photo")
        OTHER = 'other', _("Other")

    application = models.ForeignKey(
        AdmissionApplication,
        on_delete=models.CASCADE,
        related_name='application_documents'
    )
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    title = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to=application_document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

        
    def __str__(self):
        return f"{self.application.first_name} {self.application.last_name} - {self.document_type}"
    
    def clean(self):
        """ Validates the file size and type """
        if self.file and self.file.size > 5 * 1024 * 1024:
            raise ValidationError(_("File size must not exceed 5 MB."))

        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
        if not self.file.name.lower().split('.')[-1] in allowed_extensions:
            raise ValidationError(_("Only PDF and image files are allowed."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)