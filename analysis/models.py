"""
Models for performance evaluation and analysis.
"""
from django.db import models
from django.conf import settings


class Recording(models.Model):
    """
    Video/audio recording from an interview session.
    """
    session = models.ForeignKey(
        'interviews.InterviewSession',
        on_delete=models.CASCADE,
        related_name='recordings'
    )
    file = models.FileField(upload_to='recordings/%Y/%m/%d/')
    file_type = models.CharField(
        max_length=10,
        choices=[
            ('video', 'Video'),
            ('audio', 'Audio'),
        ]
    )
    transcription = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recordings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recording {self.id} - Session {self.session.id}"


class Evaluation(models.Model):
    """
    Performance evaluation results for an interview session.
    """
    session = models.OneToOneField(
        'interviews.InterviewSession',
        on_delete=models.CASCADE,
        related_name='evaluation'
    )
    
    # Content quality scores (0-100)
    structure_score = models.IntegerField(default=0)
    hypothesis_score = models.IntegerField(default=0)
    math_score = models.IntegerField(default=0)
    insight_score = models.IntegerField(default=0)
    
    # Communication scores (0-100)
    body_language_score = models.IntegerField(default=0)
    speech_pacing_score = models.IntegerField(default=0)
    presence_score = models.IntegerField(default=0)
    delivery_clarity_score = models.IntegerField(default=0)
    
    # Overall score
    overall_score = models.IntegerField(default=0)
    
    # Detailed analysis
    content_analysis = models.JSONField(default=dict)
    communication_analysis = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'evaluations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Evaluation {self.id} - Session {self.session.id} - Score: {self.overall_score}"

