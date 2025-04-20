from django.urls import path
from .views import get_academic_levels, create_study_plan_view

urlpatterns = [
    path('ajax/get-academic-levels/', get_academic_levels, name='get_academic_levels'),
    path('study-plan/create/', create_study_plan_view, name='create_study_plan'),

]
