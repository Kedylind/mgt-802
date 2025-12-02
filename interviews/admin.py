from django.contrib import admin
from .models import InterviewSession, Message


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    """Admin configuration for InterviewSession model."""
    list_display = ['id', 'user', 'mode', 'status', 'started_at', 'created_at']
    list_filter = ['mode', 'status', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model."""
    list_display = ['id', 'session', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'session__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

