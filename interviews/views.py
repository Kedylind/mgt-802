"""
Views for interview functionality.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import InterviewSession


@login_required
def interview_list_view(request):
    """List all interview sessions for the current user."""
    sessions = InterviewSession.objects.filter(user=request.user)
    return render(request, 'interviews/list.html', {'sessions': sessions})


@login_required
def interview_start_view(request):
    """Start a new interview session."""
    # This will be implemented in Phase 2
    return render(request, 'interviews/start.html')


@login_required
def interview_detail_view(request, session_id):
    """View details of a specific interview session."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    return render(request, 'interviews/detail.html', {'session': session})

