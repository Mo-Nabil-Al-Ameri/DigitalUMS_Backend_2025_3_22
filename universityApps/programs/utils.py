
def generate_program_no(department):
    from .models import AcademicProgram
    program_no = AcademicProgram.objects.filter(department=department).last().program_no + 11
    return f"{program_no}"