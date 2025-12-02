from django.contrib import admin
from .models import Recording, Evaluation


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    """Admin configuration for Recording model."""
    list_display = ['id', 'session', 'file_type', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['session__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Admin configuration for Evaluation model."""
    list_display = ['id', 'session', 'overall_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['session__user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

