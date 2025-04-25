from django.contrib import admin
from .models import AdmissionApplication, ApplicationDocument


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    readonly_fields = ('document_type', 'title', 'file', 'uploaded_at')
    can_delete = False


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'phone_number',
        'program',
        'status',
        'submission_date',
        'reviewed_by',
        'reviewed_date'
    )
    list_filter = ('status', 'program', 'archived')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'national_id')
    readonly_fields = ('submission_date', 'reviewed_date', 'reviewed_by')
    inlines = [ApplicationDocumentInline]
    ordering = ('-submission_date',)

    def full_name(self, obj):
        return obj.full_name()
    full_name.short_description = "Full Name"


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'get_applicant_name',
        'document_type',
        'title',
        'uploaded_at',
    )
    list_filter = ('document_type',)
    search_fields = ('application__first_name', 'application__last_name', 'title')

    def get_applicant_name(self, obj):
        return f"{obj.application.first_name} {obj.application.last_name}"
    get_applicant_name.short_description = "Applicant Name"
