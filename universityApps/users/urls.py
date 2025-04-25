from django.urls import path
from .views import instructor_dashboard, staff_dashboard, student_dashboard

urlpatterns = [
    path('', instructor_dashboard, name='instructor_dashboard'),
    path('', student_dashboard, name='student_dashboard'),
    path('', staff_dashboard, name='staff_dashboard'),

]
