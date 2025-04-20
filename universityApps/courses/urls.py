# courses/urls.py

from django.urls import path
from .views import CourseCreateView

urlpatterns = [
    path('create/', CourseCreateView.as_view(), name='course_create'),
]
