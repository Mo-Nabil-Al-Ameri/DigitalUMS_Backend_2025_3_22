from django.shortcuts import render, redirect,get_object_or_404
from .forms import DepartmentForm
from .models import Department
from universityApps.programs.models import AcademicProgram
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'departments/department_list.html', {'departments': departments})

def add_department(request):
    form = DepartmentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('department_list')  # Replace with your actual department list URL name
    return render(request, 'departments/add_department.html', {'form': form})

def edit_department(request, dept_no):
    department = get_object_or_404(Department, dept_no=dept_no)
    form = DepartmentForm(request.POST or None, request.FILES or None, instance=department)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('department_list')  # or wherever you want
    return render(request, 'departments/edit_department.html', {'form': form, 'department': department})

def department_detail(request, dept_no):
    department = get_object_or_404(Department, dept_no=dept_no)
    academic_program = AcademicProgram.objects.filter(department=department).order_by('program_no')
    return render(request, 'departments/department_details.html', {
        'department': department,
        'academic_program': academic_program
    })
