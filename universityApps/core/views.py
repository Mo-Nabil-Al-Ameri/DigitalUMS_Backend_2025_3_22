# public/views.py
from datetime import timedelta
from django.shortcuts import render,redirect
from django.shortcuts import render
from universityApps.programs.models import AcademicProgram
from universityApps.news.models import NewsArticle  # adjust to your news model
from django.utils.translation import get_language
from django.views import View
from django.utils import timezone
from .forms import AdmissionApplicationForm,ApplicationDocumentFormSet
from .utils import generate_verification_code, send_verification_email
from django.utils.translation import gettext_lazy as _
from django.utils.datastructures import MultiValueDict

class AdmissionMultiStepView(View):
    excluded_fields = ['full_name', 'email', 'phone_number', 'birth_date', 'national_id']

    def get(self, request):
        step = request.GET.get('step', '1')

        if step == 'verify':
            return self._get_verify_step(request)

        elif step == '2':
            return self._get_documents_step(request)

        return self._get_initial_step(request)

    def post(self, request):
        step = request.POST.get('step')
        print("🟡 Received POST with step:", request.POST.get('step'))
        print("🟡 POST DATA:", request.POST)

        if step == '1':
            return self._post_step1(request)

        elif step == 'verify':
            return self._post_verify_step(request)

        elif step == '2':
            return self._post_documents_step(request)

        return redirect('/admission/apply/')

    # ---------------------- Step 1 ----------------------
    def _get_initial_step(self, request):
        form = AdmissionApplicationForm(step='1')
        return render(request, 'public/admission_form.html', {
            'form': form,
            'step': '1',
            'excluded_fields': self.excluded_fields,
        })

    def _post_step1(self, request):
        form = AdmissionApplicationForm(request.POST, step='1')
        if form.is_valid():
            step1_data = {
                    field: (
                        form.cleaned_data[field].isoformat()
                        if hasattr(form.cleaned_data[field], 'isoformat')
                        else form.cleaned_data[field]
                    )
                    for field in self.excluded_fields
                }
            request.session['step1_data'] = step1_data
            request.session['email_verification_code'] = generate_verification_code()
            request.session['email_verification_time'] = timezone.now().isoformat()

            send_verification_email(step1_data['email'], request.session['email_verification_code'])
            return redirect('/admission/apply/?step=verify')
        else:
            print("❌ FORM INVALID")
            print("Errors:", form.errors)

        return render(request, 'public/admission_form.html', {
            'form': form,
            'step': '1',
            'excluded_fields': self.excluded_fields,
        })

    # ---------------------- Step 2: Verify ----------------------
    def _get_verify_step(self, request):
        if not request.session.get('step1_data'):
            return redirect('/admission/apply/')
        return render(request, 'public/admission_form.html', {
            'form': AdmissionApplicationForm(initial=request.session['step1_data']),
            'step': 'verify',
        })

    def _post_verify_step(self, request):
        code = request.POST.get('code')
        stored_code = request.session.get('email_verification_code')
        code_time_str = request.session.get('email_verification_time')

        if code_time_str:
            code_time = timezone.datetime.fromisoformat(code_time_str)
            if timezone.now() > code_time + timedelta(minutes=5):
                return render(request, 'public/admission_form.html', {
                    'form': AdmissionApplicationForm(initial=request.session['step1_data']),
                    'step': 'verify',
                    'error': _('رمز التحقق منتهي الصلاحية. يرجى إعادة المحاولة.')
                })

        if code == stored_code:
            return redirect('/admission/apply/?step=2')

        return render(request, 'public/admission_form.html', {
            'form': AdmissionApplicationForm(initial=request.session['step1_data']),
            'step': 'verify',
            'error': _('رمز التحقق غير صحيح.')
        })

    # 🆕 إعادة إرسال الكود
    def resend_code(self, request):
        if not request.session.get('step1_data'):
            return redirect('/admission/apply/')

        step1_data = request.session['step1_data']
        code = generate_verification_code()
        request.session['email_verification_code'] = code
        request.session['email_verification_time'] = timezone.now().isoformat()
        send_verification_email(step1_data['email'], code)

        return render(request, 'public/admission_form.html', {
            'form': AdmissionApplicationForm(initial=step1_data),
            'step': 'verify',
            'message': _('تم إرسال رمز تحقق جديد إلى بريدك الإلكتروني.')
        })

    # ---------------------- Step 3: Documents ----------------------
    def _get_documents_step(self, request):
        if not request.session.get('step1_data') or not request.session.get('email_verification_code'):
            return redirect('/admission/apply/')
        form = AdmissionApplicationForm(initial=request.session['step1_data'])
        formset = ApplicationDocumentFormSet()
        return render(request, 'public/admission_form.html', {
            'form': form,
            'document_formset': formset,
            'step': '2',
            'excluded_fields': self.excluded_fields,
        })


    def _post_documents_step(self, request):
        # 1️⃣ دمج بيانات POST مع بيانات الجلسة
        post_data = request.POST.copy()
        for key, value in request.session.get('step1_data', {}).items():
            post_data[key] = value

        # 2️⃣ بناء النموذج مع البيانات المكتملة
        form = AdmissionApplicationForm(post_data, request.FILES)
        formset = ApplicationDocumentFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            app = form.save(commit=False)
            app.status = 'submitted'
            app.submission_date = timezone.now()
            app.save()
            formset.instance = app
            formset.save()

            # 3️⃣ تنظيف الجلسة بعد الإرسال
            for key in ['step1_data', 'email_verification_code', 'email_verification_time']:
                request.session.pop(key, None)

            return redirect('public:admission_success')

        # 4️⃣ طباعة الأخطاء لتصحيحها إن وُجدت
        print("❌ form or formset not valid")
        print("Form errors:", form.errors)
        print("Formset errors:", formset.errors)

        return render(request, 'public/admission_form.html', {
            'form': form,
            'document_formset': formset,
            'step': '2',
            'excluded_fields': self.excluded_fields,
        })

def index(request):
    programs = AcademicProgram.objects.filter(programsettings__is_active=True)[:6]
    news_list = NewsArticle.objects.filter(published=True).order_by('-publish_date')[:3]
    return render(request, 'public/index.html', {
        'programs': programs,
        'news_list': news_list,
        'language': get_language()
    })

def about(request):
    return render(request, 'public/about.html')


def programs_list(request):
    programs = AcademicProgram.objects.all()
    return render(request, 'public/programs.html', {
        'programs': programs
    })

def news(request):
    return render(request, 'public/news.html')

def admissions(request):
    return render(request, 'public/admissions.html')

def contact(request):
    return render(request, 'public/contact.html')
