from django import forms
from django.forms import inlineformset_factory
from .models import StudyPlan, SemesterPlan, SemesterCourse

# نموذج الخطة الدراسية
class StudyPlanForm(forms.ModelForm):
    class Meta:
        model = StudyPlan
        fields = ['program', 'version', 'status', 'description', 'effective_from']
        widgets = {
            'effective_from': forms.DateInput(attrs={'class': 'form-control flatpickr', 'autocomplete': 'off'}),
        }

# نموذج خطة الفصل
class SemesterPlanForm(forms.ModelForm):
    class Meta:
        model = SemesterPlan
        fields = ['semester_type', 'academic_level']

# نموذج الكورس داخل الفصل
class SemesterCourseForm(forms.ModelForm):
    class Meta:
        model = SemesterCourse
        fields = ['course', 'is_required']


# forms.py (تكملة)

SemesterPlanFormSet = inlineformset_factory(
    StudyPlan, SemesterPlan, form=SemesterPlanForm,
    extra=1, can_delete=True
)

SemesterCourseFormSet = inlineformset_factory(
    SemesterPlan, SemesterCourse, form=SemesterCourseForm,
    extra=1, can_delete=True
)
