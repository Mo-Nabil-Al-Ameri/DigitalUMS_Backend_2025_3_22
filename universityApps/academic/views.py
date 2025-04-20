from django.http import JsonResponse
from universityApps.courses.models import Course
from universityApps.programs.models import AcademicLevel
from .models import StudyPlan,SemesterCourse
from django.shortcuts import render, redirect
from .forms import StudyPlanForm, SemesterPlanFormSet,SemesterCourseFormSet

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
