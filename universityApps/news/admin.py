from django.contrib import admin
from .models import NewsArticle

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'publish_date']
    search_fields = ['title', 'summary']
    prepopulated_fields = {'slug': ('title',)}
