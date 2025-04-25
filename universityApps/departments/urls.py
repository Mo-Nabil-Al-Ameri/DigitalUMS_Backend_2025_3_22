from . import views
from django.urls import path

urlpatterns = [
    path('', views.department_list, name='department_list'),
    path('add-department/', views.add_department, name='add_department'),
    path('departments/<int:dept_no>/edit/', views.edit_department, name='edit_department'),
    path('departments/<int:dept_no>/', views.department_detail, name='department_detail'),

]
