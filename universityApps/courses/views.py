from django.shortcuts import render

# Create your views here.
# courses/views.py

from django.views.generic.edit import CreateView
from .models import Course
from .forms import CourseForm
from django.urls import reverse_lazy

class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')  # أو أي صفحة تريد الرجوع إليها بعد الإضافة
