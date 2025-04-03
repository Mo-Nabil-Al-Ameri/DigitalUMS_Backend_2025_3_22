from django.contrib import admin
from .models import Department
from django import forms
from django.utils.translation import gettext_lazy as _
class DepartmentAdminForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # الحالة 1: عند إنشاء قسم جديد
        if not self.instance.pk:
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

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    form = DepartmentAdminForm
    list_display = ('dep_no','code','name','college', 'description','get_type_display')
    search_fields = ('formatted_dep_no','code','name','college', 'description','type')
    def formatted_dep_no(self, obj):
        return str(obj.dep_no).zfill(4)
    formatted_dep_no.short_description = "Department No"

    class Media:
        js = ('js/admin_department.js',)

