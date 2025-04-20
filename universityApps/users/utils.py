import os
from django.utils.timezone import now

def student_document_upload_path(instance, original_filename):
    doc_type = instance.document_type.lower()
    student_id = instance.student.student_id
    ext = os.path.splitext(original_filename)[1]
    date_path = now().strftime('%Y/%m')

    filename = f"{doc_type}_{student_id}{ext}"
    return os.path.join('students', 'documents', doc_type, student_id, date_path, filename)
