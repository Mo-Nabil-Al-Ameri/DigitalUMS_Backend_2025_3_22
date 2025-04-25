from django.contrib import admin
from django.utils.html import format_html
from .models import User, Student, FacultyMember, StaffMember, UserLog, StudentDocument, Notification
from django.utils.translation import gettext_lazy as _

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'gender', 'country')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('first_name',)

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


# @admin.register(FacultyMember)
# class FacultyMemberAdmin(admin.ModelAdmin):
#     list_display = ('get_email','get_first_name', 'get_last_name', 'Faculty_id', 'status', 'rank', 'get_department')
#     list_filter = ('status', 'rank')
#     search_fields = ('Faculty_id', 'user__first_name', 'user__last_name')

#     def get_first_name(self, obj):
#         return obj.user.first_name
#     def get_last_name(self, obj):
#         return obj.user.last_name
#     def get_department(self, obj):
#         return obj.department.name if obj.department else '-'
#     def get_email(self, obj):
#         return obj.user.email
#     get_email.short_description = 'Email'
#     get_first_name.short_description = 'First Name'
#     get_last_name.short_description = 'Last Name'
#     get_department.short_description = 'Department'

@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    list_display = ('Faculty_id', 'user', 'department', 'rank', 'status')
    search_fields = ('Faculty_id', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('status', 'rank', 'department')

    fieldsets = (
        (_("Basic Info"), {
            'fields': ('user', 'Faculty_id', 'department', 'rank', 'status')
        }),
        (_("Details"), {
            'fields': ('specialization', 'research_interests', 'publications')
        }),
    )

@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'stuff_id', 'status', 'job_title', 'get_department')
    list_filter = ('status',)
    search_fields = ('stuff_id', 'user__first_name', 'user__last_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    def get_department(self, obj):
        return obj.department.name if obj.department else '-'

    get_full_name.short_description = 'Full Name'
    get_department.short_description = 'Department'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'student_id', 'status', 'program', 'cgpa', 'total_credits_earned')
    list_filter = ('status', 'program')
    search_fields = ('student_id', 'user__first_name', 'user__last_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'document_type', 'title', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'student__user__first_name', 'student__user__last_name')

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student Name'


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'logtype', 'timestamp', 'user_agent')
    list_filter = ('logtype',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def get_user_name(self, obj):
        return obj.user.get_full_name()
    get_user_name.short_description = 'User Name'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'title', 'notification_type', 'priority', 'created_at', 'read')
    list_filter = ('notification_type', 'priority', 'read')
    search_fields = ('title', 'user__first_name', 'user__last_name', 'message')

    def get_user_name(self, obj):
        return obj.user.get_full_name()
    get_user_name.short_description = 'User Name'
