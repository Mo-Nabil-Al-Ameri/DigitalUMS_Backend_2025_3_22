
from django.urls import path
from . import views

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('<int:program_id>/', views.program_detail, name='program_detail'),
    # urls.py
    path('programs/<int:program_id>/export-pdf/',  views.export_program_pdf, name='export_program_pdf'),

]
