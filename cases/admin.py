from django.contrib import admin
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """Admin configuration for Case model."""
    list_display = ['id', 'title', 'case_type', 'generated_by', 'created_at']
    list_filter = ['case_type', 'created_at']
    search_fields = ['title', 'prompt']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

