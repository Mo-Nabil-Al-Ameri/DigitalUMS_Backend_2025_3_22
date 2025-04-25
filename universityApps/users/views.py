from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def instructor_dashboard(request):
    return render(request, 'instructor/dashboard.html')

@login_required
def student_dashboard(request):
    return render(request, 'student/dashboard.html')

@login_required
def staff_dashboard(request):
    return render(request, 'staff/dashboard.html')
