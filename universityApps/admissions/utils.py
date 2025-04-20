import os
from django.utils.timezone import now
from universityApps.users.models import Student
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def send_acceptance_email(to_email, full_name, program_name, username, student_portal_url=None):
    """
    إرسال بريد تأكيد القبول للطالب
    """
    subject = _("🎓 تم قبولك في برنامج %(program)s") % {'program': program_name}
    from_email = settings.DEFAULT_FROM_EMAIL
    admin_email = getattr(settings, 'ADMISSIONS_EMAIL', from_email)

    context = {
        'full_name': full_name,
        'program_name': program_name,
        'username': username,
        'student_portal_url': student_portal_url or 'https://university.edu/student-portal',
    }

    # المحتوى النصي
    text_content = render_to_string("emails/admission_accepted.txt", context)

    # المحتوى HTML
    html_content = render_to_string("emails/admission_accepted.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email], cc=[admin_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_rejection_email(to_email, full_name, program_name, reason=None):
    """
    إرسال بريد إشعار بالرفض للطالب
    """
    subject = _("❌ نتيجة طلب الالتحاق ببرنامج %(program)s") % {'program': program_name}
    from_email = settings.DEFAULT_FROM_EMAIL
    admin_email = getattr(settings, 'ADMISSIONS_EMAIL', from_email)

    context = {
        'full_name': full_name,
        'program_name': program_name,
        'reason': reason,
    }

    # الرسالة النصية
    text_content = render_to_string("emails/admission_rejected.txt", context)

    # الرسالة HTML
    html_content = render_to_string("emails/admission_rejected.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email], cc=[admin_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def application_document_upload_path(instance, original_filename):
    doc_type = instance.document_type.lower()
    name = instance.application.full_name()
    ext = os.path.splitext(original_filename)[1]
    date_path = now().strftime('%Y/%m')

    filename = f"{doc_type}_{name}{ext}"
    return os.path.join('Applications', 'documents', name ,doc_type, date_path, filename)

def generate_student_id(program):
    current_year = now().year
    count = Student.objects.filter(program=program, admission_date__year=current_year).count() + 1

    return f"{current_year}{program.department.dept_no}{count:03}"