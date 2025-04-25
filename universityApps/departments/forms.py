from django import forms
from .models import Department
from django.utils.translation import gettext_lazy as _
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # الحالة 1: عند إنشاء قسم جديد
        if not self.instance.dept_no:
            self.fields['college'].required = False

        # الحالة 2: عند التعديل
        if self.instance and self.instance.type == 'administrative':
            self.fields['college'].required = False

    def clean(self):
        cleaned_data = super().clean()
        dept_type = cleaned_data.get('type')
        college = cleaned_data.get('college')

        if dept_type == 'academic' and not college:
             self.add_error( 'college', _("يجب اختيار الكلية عند اختيار قسم أكاديمي."))
        if dept_type == 'administrative' and college:
            self.add_error('college',_("القسم الإداري لا يجب أن يكون مرتبطًا بكلية."))

        return cleaned_data
