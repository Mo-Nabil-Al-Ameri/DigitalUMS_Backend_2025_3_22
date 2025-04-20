from django import forms
from django.contrib import admin
from .models import Subject,Course, Module, Content, Text, File, Image, Video

# --------- Custom Form for Subject ---------
class SubjectAdminForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ❌ لا داعي لإخفاء الحقول بالسيرفر

# --------- Admin Class for Subject ---------
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = ('name', 'code', 'type', 'college', 'department', 'total_courses')
    list_filter = ('type', 'college', 'department')
    search_fields = ('name', 'code')
    ordering = ('name',)
    list_select_related = ('college', 'department')
    readonly_fields = ('code', 'slug')

    class Media:
        js = ('admin/js/subject_dynamic_fields.js',)  # JavaScript مخصص لإدارة الإخفاء والإظهار ديناميكياً

# --------- Inline for Content ---------
class ContentInline(admin.TabularInline):
    model = Content
    extra = 0
    fields = ('content_type', 'object_id', 'order')
    ordering = ('order',)
    show_change_link = True

# --------- Inline for Module ---------
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ('title', 'description', 'order')
    ordering = ('order',)
    show_change_link = True


# --------- Course Admin ---------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id','code', 'name', 'subject', 'credits', 'course_type', 'is_active', 'created_at','display_prerequisites')
    list_filter = ('course_type', 'is_active', 'subject')
    search_fields = ('code', 'name', 'subject__name')
    ordering = ('-created_at', 'code')
    list_select_related = ('subject',)
    filter_horizontal = ('prerequisites',)
    readonly_fields = ('code', 'slug', 'created_at', 'updated_at')
    inlines = [ModuleInline]
    def display_prerequisites(self, obj):
        return ", ".join([str(pr.name) for pr in obj.prerequisites.all() if pr.name])
    display_prerequisites.short_description = "Prerequisites"

# --------- Module Admin ---------
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__name')
    ordering = ('course', 'order')
    list_select_related = ('course',)
    inlines = [ContentInline]

# --------- Content Admin ---------
@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('module', 'content_type', 'object_id', 'order')
    list_filter = ('content_type',)
    search_fields = ('module__title',)
    ordering = ('module', 'order')
    list_select_related = ('module', 'content_type')

# --------- ItemBase Subclasses Admins ---------
@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__email')
    ordering = ('created_at',)

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__email')
    ordering = ('created_at',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__email')
    ordering = ('created_at',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__email')
    ordering = ('created_at',)
