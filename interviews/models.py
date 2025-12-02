"""
Models for interview sessions and messages.
"""
from django.db import models
from django.conf import settings


class InterviewSession(models.Model):
    """
    Represents an interview session with a candidate.
    """
    INTERVIEWER_LED = 'interviewer_led'
    CANDIDATE_LED = 'candidate_led'
    PM_PRODUCT_CASE = 'pm_product_case'
    
    MODE_CHOICES = [
        (INTERVIEWER_LED, 'Interviewer-Led'),
        (CANDIDATE_LED, 'Candidate-Led'),
        (PM_PRODUCT_CASE, 'PM Product Case'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_sessions'
    )
    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interview_sessions'
    )
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(
        max_length=20,
        default='not_started',
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('abandoned', 'Abandoned'),
        ]
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'interview_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Interview {self.id} - {self.user.username} - {self.get_mode_display()}"


class Message(models.Model):
    """
    Chat messages in an interview session.
    """
    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User'),
            ('assistant', 'Assistant'),
            ('system', 'System'),
        ]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role} - {self.session.id} - {self.created_at}"

