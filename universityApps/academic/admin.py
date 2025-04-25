from django.contrib import admin

from universityApps.programs.models import AcademicLevel
from .models import StudyPlan, SemesterPlan, SemesterCourse,AcademicYear, Semester ,LectureBroadcast,Classroom
from django import forms
class SemesterPlanForm(forms.ModelForm):
    class Meta:
        model = SemesterPlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # لو الفورم يتم تحرير كائن موجود (edit mode)
        if self.instance and self.instance.pk:
            if self.instance.study_plan and self.instance.study_plan.program:
                program = self.instance.study_plan.program
                self.fields['academic_level'].queryset = AcademicLevel.objects.filter(program=program)
        
        # لو الفورم يتم إنشاؤه لأول مرة (new object)
        elif 'study_plan' in self.data:
            try:
                study_plan_id = int(self.data.get('study_plan'))
                from universityApps.academic.models import StudyPlan  # استدعاء StudyPlan
                study_plan = StudyPlan.objects.get(id=study_plan_id)
                if study_plan.program:
                    self.fields['academic_level'].queryset = AcademicLevel.objects.filter(program=study_plan.program)
            except (ValueError, TypeError, StudyPlan.DoesNotExist):
                pass

# --------- SemesterCourse Inline ---------
class SemesterCourseInline(admin.TabularInline):
    model = SemesterCourse
    extra = 0
    fields = ('course', 'is_required', 'order', 'code')
    readonly_fields = ('code',)
    ordering = ('order',)
    show_change_link = True
    autocomplete_fields = ('course',)

# --------- SemesterPlan Admin ---------
class SemesterPlanAdmin(admin.ModelAdmin):
    form = SemesterPlanForm
    list_display = ('study_plan', 'academic_level', 'semester_type','order')
    list_filter = ('semester_type', 'academic_level')
    search_fields = ('study_plan__name', 'academic_level__name')
    ordering = ('academic_level', 'semester_type')
    inlines = [SemesterCourseInline]
    list_select_related = ('study_plan', 'academic_level')

    class Media:
        js = ('admin/js/semester_plan_dynamic.js',)

admin.site.register(SemesterPlan, SemesterPlanAdmin)

# --------- StudyPlan Admin ---------
@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('program', 'name', 'version', 'status', 'effective_from')
    list_filter = ('status', 'program__degree_level')
    search_fields = ('program__name', 'name')
    ordering = ('-effective_from', 'version')
    list_select_related = ('program',)

# --------- SemesterCourse Admin ---------
@admin.register(SemesterCourse)
class SemesterCourseAdmin(admin.ModelAdmin):
    list_display = ('semester_plan', 'course', 'order', 'is_required', 'code',)
    list_filter = ('is_required', 'semester_plan__semester_type')
    search_fields = ('course__name', 'semester_plan__study_plan__name')
    ordering = ('semester_plan', 'order')
    list_select_related = ('semester_plan', 'course')


# --------- Semester Inline ---------
class SemesterInline(admin.TabularInline):
    model = Semester
    extra = 0
    fields = ('semester_type',)
    ordering = ('semester_type',)
    show_change_link = True

# --------- AcademicYear Admin ---------
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current', 'created_at')
    list_filter = ('is_current',)
    search_fields = ('name',)
    ordering = ('-start_date',)
    inlines = [SemesterInline]
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        # تأكد أن لا يوجد أكثر من سنة حالية
        if obj.is_current:
            AcademicYear.objects.exclude(pk=obj.pk).update(is_current=False)
        super().save_model(request, obj, form, change)

# --------- Semester Admin ---------
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'semester_type')
    list_filter = ('semester_type', 'academic_year')
    search_fields = ('academic_year__name',)
    ordering = ('academic_year', 'semester_type')
    list_select_related = ('academic_year',)


@admin.register(LectureBroadcast)
class LectureBroadcastAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'status', 'stream_key', 'viewer_count']
    readonly_fields = ['get_rtmp_url', 'get_hls_url', 'playback_token', 'token_expiry']
    actions = ['generate_tokens']

    def get_rtmp_url(self, obj):
        return obj.get_rtmp_url()
    get_rtmp_url.short_description = "RTMP URL (OBS)"

    def get_hls_url(self, obj):
        return obj.get_hls_url()
    get_hls_url.short_description = "HLS Stream URL"

    @admin.action(description="Generate playback token")
    def generate_tokens(self, request, queryset):
        for obj in queryset:
            obj.generate_token()

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'floor', 'capacity', 'is_lab', 'is_virtual', 'is_active']
    list_filter = ['is_lab', 'is_virtual', 'building']
    search_fields = ['name', 'building']
