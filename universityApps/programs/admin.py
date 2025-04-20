from django.contrib import admin
from .models import AcademicProgram, ProgramSettings, AcademicLevel

class ProgramSettingsInline(admin.StackedInline):
    model = ProgramSettings
    extra = 0
    can_delete = False
    verbose_name = "Program Setting"
    verbose_name_plural = "Program Settings"

    # حماية من إنشاء أكثر من واحد لأن العلاقة OneToOne
    def has_add_permission(self, request, obj):
        if obj and ProgramSettings.objects.filter(program=obj).exists():
            return False
        return True

@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ('program_no', 'code', 'name', 'degree_level', 'study_system', 'department', 'is_active_program')
    list_filter = ('degree_level', 'study_system', 'department')
    search_fields = ('code', 'name', 'department__name')
    ordering = ('program_no',)
    list_select_related = ('department',)
    inlines = [ProgramSettingsInline]
    def is_active_program(self, obj):
        return obj.programsettings.is_active if hasattr(obj, 'programsettings') else False
    is_active_program.boolean = True
    is_active_program.short_description = 'Active'


@admin.register(ProgramSettings)
class ProgramSettingsAdmin(admin.ModelAdmin):
    list_display = ('program', 'standard_duration_years', 'max_duration_years', 'credits_per_semester', 'summer_semester_enabled', 'min_cgpa_required', 'is_active')
    list_filter = ('is_active', 'summer_semester_enabled')
    search_fields = ('program__name', 'program__code')
    ordering = ('program',)
    list_select_related = ('program',)


@admin.register(AcademicLevel)
class AcademicLevelAdmin(admin.ModelAdmin):
    list_display = ('program', 'level_number', 'name', 'required_credits', 'prerequisite_level_display')
    list_filter = ('program',)
    search_fields = ('program__name', 'name')
    ordering = ('program', 'level_number')
    list_select_related = ('program', 'prerequisite_level')

    def prerequisite_level_display(self, obj):
        return obj.prerequisite_level.name if obj.prerequisite_level else "-"
    prerequisite_level_display.short_description = 'Prerequisite Level'
