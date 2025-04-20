# courses/forms.py

from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['subject','name', 'credits', 'name','practice_hours', 'hours_lecture', 'hours_lab', ]  # عدّل الحقول حسب ما هو موجود في الموديل
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
