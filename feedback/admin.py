from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin configuration for Feedback model."""
    list_display = ['id', 'evaluation', 'created_at']
    search_fields = ['summary', 'evaluation__session__user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

