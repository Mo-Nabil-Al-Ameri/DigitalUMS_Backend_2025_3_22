from django.shortcuts import render
from django.urls import path
from . import views
from django.views.generic import TemplateView  # ✅

app_name = 'public'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('programs/', views.programs_list, name='programs'),
    path('news/', views.news, name='news'),
    path('admissions/', views.admissions, name='admissions'),
    path('contact/', views.contact, name='contact'),
    path('admission/apply/', views.AdmissionMultiStepView.as_view(), name='apply_for_admission'),
    path('admission/success/', lambda request: render(request, 'public/admission_success.html'), name='admission_success'),
    path('apply/resend/', views.AdmissionMultiStepView.as_view(), name='resend_verification_code'),

]
