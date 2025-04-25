from django.urls import path
from .views import get_academic_levels, create_study_plan_view, watch_live,end_session,go_live,export_attendance_csv,upcoming_live_lectures

urlpatterns = [
    path('ajax/get-academic-levels/', get_academic_levels, name='get_academic_levels'),
    path('study-plan/create/', create_study_plan_view, name='create_study_plan'),
    path('watch/<str:stream_key>/<str:token>/', watch_live, name='watch_live'),
    # path('instructor/dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('instructor/go-live/<int:schedule_id>/', go_live, name='go_live'),
    path('instructor/end-session/<int:schedule_id>/', end_session, name='end_session'),
    path('student/upcoming-live/', upcoming_live_lectures, name='upcoming_live_lectures'),
    path('instructor/export-attendance/<int:broadcast_id>/', export_attendance_csv, name='export_attendance'),

]
