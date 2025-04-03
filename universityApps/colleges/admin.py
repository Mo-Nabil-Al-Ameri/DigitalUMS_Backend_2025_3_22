from django.contrib import admin
from .models import College

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
     list_display = ('college_no','code', 'name', 'description')
     search_fields = ('college_no','code', 'name', 'description')
     ordering = ['code','college_no']
     list_per_page = 10
     list_max_show_all = 100
     