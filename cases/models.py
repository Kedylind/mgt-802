"""
Models for case generation and management.
"""
from django.db import models
from django.conf import settings


class Case(models.Model):
    """
    Represents a generated case interview scenario.
    """
    CONSULTING = 'consulting'
    PRODUCT_MANAGEMENT = 'product_management'
    
    CASE_TYPE_CHOICES = [
        (CONSULTING, 'Consulting'),
        (PRODUCT_MANAGEMENT, 'Product Management'),
    ]
    
    title = models.CharField(max_length=200)
    case_type = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES)
    prompt = models.TextField(help_text='The main case prompt/question')
    context = models.JSONField(
        default=dict,
        help_text='Additional context and background information'
    )
    exhibits = models.JSONField(
        default=list,
        help_text='List of exhibits (tables, charts, data) for the case'
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_cases'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cases'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_case_type_display()}"

