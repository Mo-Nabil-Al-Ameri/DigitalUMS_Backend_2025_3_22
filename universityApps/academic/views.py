from django.http import JsonResponse
from universityApps.academic.models import LiveAttendanceLog
from universityApps.courses.models import Course
from universityApps.programs.models import AcademicLevel
from .models import StudyPlan,SemesterCourse
from django.shortcuts import render, redirect,get_object_or_404
from .forms import StudyPlanForm, SemesterPlanFormSet,SemesterCourseFormSet
from django.http import HttpResponseForbidden
from .models import LectureBroadcast
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import LectureBroadcast, GroupSchedule
import csv
from django.http import HttpResponse

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Instructors').exists())
def go_live(request, schedule_id):
    schedule = get_object_or_404(GroupSchedule, id=schedule_id, instructor=request.user.facultyprofile)
    broadcast = schedule.broadcast
    broadcast.status = LectureBroadcast.Status.LIVE
    broadcast.start_time = timezone.now()
    broadcast.generate_token()
    broadcast.save()
    return redirect('instructor_dashboard')


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Instructors').exists())
def end_session(request, schedule_id):
    broadcast = get_object_or_404(LectureBroadcast, schedule_id=schedule_id)
    broadcast.status = LectureBroadcast.Status.ENDED
    broadcast.end_time = timezone.now()
    broadcast.save()
    return redirect('instructor_dashboard')

@login_required
def watch_live(request, stream_key, token):
    broadcast = get_object_or_404(LectureBroadcast, stream_key=stream_key)

    if not broadcast.is_token_valid(token):
        return HttpResponseForbidden("Invalid or expired token.")

    student = request.user.studentprofile
    LiveAttendanceLog.objects.get_or_create(broadcast=broadcast, student=student)

    return render(request, 'broadcast/watch_live.html', {'broadcast': broadcast})

@login_required
def export_attendance_csv(request, broadcast_id):
    broadcast = get_object_or_404(LectureBroadcast, id=broadcast_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{broadcast.id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student', 'Join Time', 'Leave Time'])
    for log in broadcast.logs.all():
        writer.writerow([log.student.user.get_full_name(), log.join_time, log.leave_time or '—'])
    return response

# def is_instructor(user):
#     return hasattr(user, 'facultyprofile')  # or your condition

# @login_required
# @user_passes_test(is_instructor)
# def instructor_dashboard(request):
#     schedules = GroupSchedule.objects.filter(instructor=request.user.facultyprofile)
#     return render(request, 'instructor/dashboard.html', {'schedules': schedules})

# @login_required
# @user_passes_test(is_instructor)
# def go_live(request, schedule_id):
#     schedule = get_object_or_404(GroupSchedule, id=schedule_id, instructor=request.user.facultyprofile)
#     broadcast = schedule.broadcast
#     broadcast.status = LectureBroadcast.BroadcastStatus.LIVE
#     broadcast.start_time = timezone.now()
#     broadcast.save()
#     return redirect('instructor_dashboard')

# @login_required
# @user_passes_test(is_instructor)
# def end_session(request, schedule_id):
#     schedule = get_object_or_404(GroupSchedule, id=schedule_id, instructor=request.user.facultyprofile)
#     broadcast = schedule.broadcast
#     broadcast.status = LectureBroadcast.BroadcastStatus.ENDED
#     broadcast.end_time = timezone.now()
#     broadcast.save()
#     return redirect('instructor_dashboard')

# from .models import LiveAttendanceLog
# from django.contrib.auth.decorators import login_required
# from .models import GroupSchedule
# from datetime import timedelta

# @login_required
def upcoming_live_lectures(request):
    student = request.user.studentprofile
    today = timezone.now().date()

    group = getattr(student, 'group', None)
    if not group:
        return render(request, 'broadcast/upcoming.html', {"lectures": [], "error": "You are not assigned to a group."})

    lectures = GroupSchedule.objects.filter(
        group=group.group,
        is_online=True,
        broadcast__isnull=False,
        broadcast__status__in=['scheduled', 'live'],
        semester__academic_year__start_date__lte=today
    ).select_related('broadcast', 'semester_course', 'semester_course__course')

    return render(request, 'broadcast/upcoming.html', {"lectures": lectures})

# @login_required
# @user_passes_test(is_instructor)
# def export_attendance_csv(request, broadcast_id):
#     broadcast = get_object_or_404(LectureBroadcast, id=broadcast_id, schedule__instructor=request.user.facultyprofile)

#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="attendance_{broadcast.id}.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['Student ID', 'Full Name', 'Join Time', 'Leave Time'])

#     for log in broadcast.attendance_logs.select_related('student'):
#         writer.writerow([
#             log.student.student_id,
#             log.student.user.get_full_name(),
#             log.join_time.strftime('%Y-%m-%d %H:%M'),
#             log.leave_time.strftime('%Y-%m-%d %H:%M') if log.leave_time else 'Still Live'
#         ])

#     return response

# def watch_live(request, stream_key, token):
#     broadcast = get_object_or_404(LectureBroadcast, stream_key=stream_key)

#     if not broadcast.is_token_valid(token):
#         return HttpResponseForbidden("Invalid or expired token.")

#     if request.user.is_authenticated and hasattr(request.user, 'studentprofile'):
#         LiveAttendanceLog.objects.get_or_create(broadcast=broadcast, student=request.user.studentprofile)

#     return render(request, "broadcast/watch_live.html", {"broadcast": broadcast})

def get_academic_levels(request):
    study_plan_id = request.GET.get('study_plan')
    data = []
    if study_plan_id:
        try:
            study_plan = StudyPlan.objects.get(id=study_plan_id)
            levels = AcademicLevel.objects.filter(program=study_plan.program).values('id', 'name')
            data = list(levels)
        except StudyPlan.DoesNotExist:
            pass
    return JsonResponse({'levels': data})

# views.py
from django.shortcuts import render, redirect
from .forms import StudyPlanForm, SemesterPlanFormSet
from .models import StudyPlan, SemesterPlan, SemesterCourse
from  universityApps.courses.models import Course

def create_study_plan_view(request):
    if request.method == 'POST':
        study_form = StudyPlanForm(request.POST)
        semester_formset = SemesterPlanFormSet(request.POST, prefix='semesters')

        if study_form.is_valid() and semester_formset.is_valid():
            study_plan = study_form.save()
            semester_formset.instance = study_plan
            semesters = semester_formset.save()

            # حفظ المقررات لكل فصل
            for idx, semester in enumerate(semesters):
                i = 0
                while True:
                    course_key = f'courses-{idx}-{i}-course'
                    required_key = f'courses-{idx}-{i}-is_required'

                    if course_key not in request.POST:
                        break

                    course_id = request.POST.get(course_key)
                    is_required = request.POST.get(required_key) == 'on'

                    if course_id:
                        SemesterCourse.objects.create(
                            semester_plan=semester,
                            course_id=course_id,
                            is_required=is_required
                        )
                    i += 1

            return redirect('study_plan_success')  # حدد وجهة النجاح أو عدلها حسب التطبيق
    else:
        study_form = StudyPlanForm()
        semester_formset = SemesterPlanFormSet(prefix='semesters')

    context = {
        'study_form': study_form,
        'semester_formset': semester_formset,
        'courses': Course.objects.all(),  # عرض المقررات مباشرة
    }

    return render(request, 'academic/study_plan_form.html', context)
