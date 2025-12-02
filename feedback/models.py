"""
Models for coaching feedback.
"""
from django.db import models


class Feedback(models.Model):
    """
    Coaching feedback and recommendations for an interview session.
    """
    evaluation = models.OneToOneField(
        'analysis.Evaluation',
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    summary = models.TextField(help_text='Overall feedback summary')
    strengths = models.JSONField(
        default=list,
        help_text='List of identified strengths'
    )
    areas_for_improvement = models.JSONField(
        default=list,
        help_text='List of areas that need improvement'
    )
    recommendations = models.JSONField(
        default=list,
        help_text='Specific recommendations and drills'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback {self.id} - Evaluation {self.evaluation.id}"

