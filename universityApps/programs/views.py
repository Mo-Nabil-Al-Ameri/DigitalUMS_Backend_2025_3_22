
from django.shortcuts import render, get_object_or_404
from .models import AcademicProgram
from .models import AcademicLevel

def program_list(request):
    programs = AcademicProgram.objects.all()
    return render(request, 'programs/program_list.html', {'programs': programs})

def program_detail(request, program_id):
    program = get_object_or_404(AcademicProgram, id=program_id)
    program_levels = AcademicLevel.objects.filter(program=program).order_by('level_number')
    return render(request, 'programs/program_detail.html', {
        'program': program,
        'program_levels': program_levels
    })
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from .models import AcademicProgram

def export_program_pdf(request, program_id):
    program = get_object_or_404(AcademicProgram, id=program_id)

    levels = program.levels.prefetch_related(
        'semester_plans__semester_courses__course'
    )

    electives = []
    max_courses = 0

    for level in levels:
        semesters = level.get_semesters()
        level.semesters = semesters  # لإتاحة access في القالب

        # تحديث المتطلبات الاختيارية
        for semester in semesters:
            num_courses = semester.semester_courses.count()
            max_courses = max(max_courses, num_courses)

            electives += [
                sc.course for sc in semester.semester_courses.filter(is_required=False)
            ]

    html = render_to_string('programs/pdf_template.html', {
        'program': program,
        'program_levels': levels,
        'electives': electives,
        'range8': range(max_courses),  # اسم المتغير اختياري
    })

    pdf_file = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()

    return HttpResponse(
        pdf_file,
        content_type='application/pdf',
        headers={'Content-Disposition': f'inline; filename="{program.name}_plan.pdf"'}
    )
