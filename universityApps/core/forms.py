# admissions/forms.py
from django import forms
from universityApps.admissions.models import AdmissionApplication, ApplicationDocument
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
class AdmissionApplicationForm(forms.ModelForm):
    full_name = forms.CharField(
    label=_('Full Name'),
    max_length=250,
    widget=forms.TextInput(attrs={'class': 'form-control'})
)

    def __init__(self, *args, **kwargs):
        step = kwargs.pop('step', None)
        super().__init__(*args, **kwargs)
        if self.instance and (self.instance.first_name or self.instance.last_name):
            self.initial['full_name'] = f"{self.instance.first_name} {self.instance.last_name}"
        # الحقول الظاهرة فقط في الخطوة 1
        step1_fields = ['full_name', 'email', 'phone_number', 'birth_date', 'national_id']
        self.order_fields(['full_name'] + [n for n in self.fields if n != 'full_name'])

        if step == '1':
            for field_name in self.fields:
                if field_name not in step1_fields:
                    self.fields[field_name].required = False

    class Meta:
        model = AdmissionApplication
        exclude = ['first_name', 'last_name','status', 'reviewed_by', 'reviewed_date', 'archived', 'notes']
        widgets = {
            'birth_date': forms.DateInput(
                attrs={'class': 'form-control flatpickr', 'placeholder': 'YYYY-MM-DD', 'autocomplete': 'off'}
            ),
            'date_obtained': forms.DateInput(attrs={
                'class': 'form-control flatpickr',
                'placeholder': 'yyyy-mm-dd',
                'autocomplete': 'off'
            }),
        }

    def clean_full_name(self):
        full = self.cleaned_data.get('full_name', '').strip()
        parts = full.split()  # تقسم على المسافات :contentReference[oaicite:4]{index=4}
        if len(parts) < 4:
            raise forms.ValidationError(
                _('Please enter at least four names.'),
                code='full_names_min'
            )
        return full

    def save(self, commit=True):
        # حفظ جزئي للحصول على instance قبل الكتابة إلى first_name/last_name
        instance = super().save(commit=False)  # ModelForm.save(commit=False) :contentReference[oaicite:1]{index=1}
        parts = self.cleaned_data['full_name'].split()
        instance.first_name = parts[0]
        instance.last_name  = ' '.join(parts[1:])
        if commit:
            instance.save()
        return instance

# نموذج المستندات المرتبطة
ApplicationDocumentFormSet = inlineformset_factory(
    AdmissionApplication,
    ApplicationDocument,
    fields=['document_type', 'title', 'file'],
    extra=3,
    can_delete=False
)
