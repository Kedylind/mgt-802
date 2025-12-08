"""
Views for interview functionality.
"""
import os
import json
from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import InterviewSession


@login_required
def interview_list_view(request: HttpRequest) -> HttpResponse:
    """List all interview sessions for the current user."""
    sessions = InterviewSession.objects.filter(user=request.user)
    return render(request, 'interviews/list.html', {'sessions': sessions})


@login_required
def interview_start_view(request):
    """Start a new interview session."""
    from cases.models import Case
    
    if request.method == 'POST':
        case_id = request.POST.get('case_id')
        mode = request.POST.get('mode')
        
        # Validate inputs
        try:
            case = Case.objects.get(id=case_id)
        except Case.DoesNotExist:
            return redirect('interview_start')
        
        # Create interview session
        session = InterviewSession.objects.create(
            user=request.user,
            case=case,
            mode=mode,
            status='in_progress'
        )
        
        return redirect('interview_detail', session_id=session.id)
    
    # GET request - show form
    cases = Case.objects.all().order_by('-created_at')
    return render(request, 'interviews/start.html', {'cases': cases})


@login_required
def interview_detail_view(request, session_id):
    """View details of a specific interview session."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    # If interview is completed, get evaluation and feedback
    evaluation = None
    feedback = None
    evaluation_json = None
    if session.status == 'completed' and hasattr(session, 'evaluation'):
        evaluation = session.evaluation
        feedback = evaluation.feedback
        # Serialize evaluation data for JavaScript
        evaluation_json = json.dumps({
            'structure_score': evaluation.structure_score,
            'hypothesis_score': evaluation.hypothesis_score,
            'math_score': evaluation.math_score,
            'insight_score': evaluation.insight_score,
            'overall_score': evaluation.overall_score,
            'strengths': feedback.strengths if feedback else [],
            'areas_for_improvement': feedback.areas_for_improvement if feedback else [],
            'detailed_analysis': feedback.summary if feedback else ''
        })
    
    return render(request, 'interviews/detail.html', {
        'session': session,
        'evaluation': evaluation,
        'feedback': feedback,
        'evaluation_json': evaluation_json
    })


@login_required
def evaluate_interview_view(request, session_id):
    """Evaluate a completed interview and generate feedback."""
    from analysis.models import Evaluation
    from feedback.models import Feedback
    from agents.evaluator import EvaluatorAgent
    from agents.coach import CoachAgent
    
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    # Check if already evaluated
    if hasattr(session, 'evaluation'):
        return redirect('feedback_view', session_id=session_id)
    
    # Get conversation history
    messages = session.messages.all().values('role', 'content')
    conversation_history = list(messages)
    
    # Get case data
    if not session.case:
        return redirect('interview_detail', session_id=session_id)
    
    case_data = {
        'title': session.case.title,
        'prompt': session.case.prompt,
        'context': session.case.context,
        'exhibits': session.case.exhibits,
        'case_type': session.case.case_type
    }
    
    # Run evaluation
    evaluator = EvaluatorAgent()
    evaluation_results = evaluator.evaluate_interview(case_data, conversation_history)
    
    # Save evaluation
    evaluation = Evaluation.objects.create(
        session=session,
        structure_score=evaluation_results.get('structure_score', 0),
        hypothesis_score=evaluation_results.get('hypothesis_score', 0),
        math_score=evaluation_results.get('math_score', 0),
        insight_score=evaluation_results.get('insight_score', evaluation_results.get('insights_score', 0)),
        overall_score=evaluation_results.get('overall_score', 0),
        content_analysis=evaluation_results
    )
    
    # Generate coaching feedback
    coach = CoachAgent()
    coaching_results = coach.generate_feedback(evaluation_results, case_data)
    
    # Save feedback
    Feedback.objects.create(
        evaluation=evaluation,
        summary=coaching_results['summary'],
        strengths=coaching_results['strengths'],
        areas_for_improvement=coaching_results['areas_for_improvement'],
        recommendations=coaching_results['recommendations']
    )
    
    return redirect('feedback_view', session_id=session_id)


@login_required
def feedback_view(request, session_id):
    """View feedback for a completed interview."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if not hasattr(session, 'evaluation'):
        return redirect('evaluate_interview', session_id=session_id)
    
    evaluation = session.evaluation
    feedback = evaluation.feedback
    
    return render(request, 'interviews/feedback.html', {
        'session': session,
        'evaluation': evaluation,
        'feedback': feedback
    })


@login_required
@require_http_methods(["POST"])
def evaluate_interview_inline_view(request: HttpRequest, session_id: int) -> JsonResponse:
    """
    Evaluate an interview and return results as JSON for inline display.
    
    Args:
        request: HTTP request object
        session_id: ID of the interview session
        
    Returns:
        JsonResponse with evaluation results
    """
    from analysis.models import Evaluation
    from feedback.models import Feedback
    from agents.evaluator import EvaluatorAgent
    from agents.coach import CoachAgent
    
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    # Check if already evaluated
    if hasattr(session, 'evaluation'):
        evaluation = session.evaluation
        feedback = evaluation.feedback if hasattr(evaluation, 'feedback') else None
        return JsonResponse({
            'structure_score': evaluation.structure_score,
            'hypothesis_score': evaluation.hypothesis_score,
            'math_score': evaluation.math_score,
            'insight_score': evaluation.insight_score,
            'overall_score': evaluation.overall_score,
            'strengths': feedback.strengths if feedback else [],
            'areas_for_improvement': feedback.areas_for_improvement if feedback else [],
            'detailed_analysis': feedback.summary if feedback else ''
        })
    
    # Get conversation history
    messages = session.messages.all().values('role', 'content')
    conversation_history = list(messages)
    
    # Get case data
    if not session.case:
        return JsonResponse({'error': 'No case associated with this interview'}, status=400)
    
    case_data = {
        'title': session.case.title,
        'prompt': session.case.prompt,
        'context': session.case.context,
        'exhibits': session.case.exhibits,
        'case_type': session.case.case_type
    }
    
    # Run evaluation
    evaluator = EvaluatorAgent()
    evaluation_results = evaluator.evaluate_interview(case_data, conversation_history)
    
    # Save evaluation
    evaluation = Evaluation.objects.create(
        session=session,
        structure_score=evaluation_results.get('structure_score', 0),
        hypothesis_score=evaluation_results.get('hypothesis_score', 0),
        math_score=evaluation_results.get('math_score', 0),
        insight_score=evaluation_results.get('insight_score', evaluation_results.get('insights_score', 0)),
        overall_score=evaluation_results.get('overall_score', 0),
        content_analysis=evaluation_results
    )
    
    # Generate coaching feedback
    coach = CoachAgent()
    coaching_results = coach.generate_feedback(evaluation_results, case_data)
    
    # Save feedback
    Feedback.objects.create(
        evaluation=evaluation,
        summary=coaching_results['summary'],
        strengths=coaching_results['strengths'],
        areas_for_improvement=coaching_results['areas_for_improvement'],
        recommendations=coaching_results['recommendations']
    )
    
    # Return the coaching results (not raw evaluation results)
    return JsonResponse({
        'structure_score': evaluation.structure_score,
        'hypothesis_score': evaluation.hypothesis_score,
        'math_score': evaluation.math_score,
        'insight_score': evaluation.insight_score,
        'overall_score': evaluation.overall_score,
        'strengths': coaching_results['strengths'],
        'areas_for_improvement': coaching_results['areas_for_improvement'],
        'detailed_analysis': coaching_results['summary']
    })


@login_required
@require_http_methods(["POST"])
def complete_interview_view(request: HttpRequest, session_id: int) -> JsonResponse:
    """
    Mark an interview session as completed.
    
    Args:
        request: HTTP request object
        session_id: ID of the interview session
        
    Returns:
        JsonResponse with success status
    """
    from django.utils import timezone
    
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    # Check if already completed
    if session.status == 'completed':
        return JsonResponse({'success': True, 'message': 'Interview already completed'})
    
    # Mark as completed
    session.status = 'completed'
    session.current_phase = 'completed'
    session.completed_at = timezone.now()
    session.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Interview completed successfully'
    })


@login_required
@require_http_methods(["POST"])
def upload_recording_view(request: HttpRequest, session_id: int) -> JsonResponse:
    """
    Handle recording file upload and trigger transcription.
    
    Args:
        request: HTTP request object
        session_id: ID of the interview session
        
    Returns:
        JsonResponse with success status and recording ID
    """
    from analysis.models import Recording
    
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if 'recording' not in request.FILES:
        return JsonResponse({'error': 'No recording file provided'}, status=400)
    
    recording_file = request.FILES['recording']
    
    # Validate file size (max 100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    if recording_file.size > max_size:
        return JsonResponse({'error': 'File too large. Maximum size is 100MB.'}, status=400)
    
    # Determine file type
    content_type = recording_file.content_type or ''
    file_type = 'video' if content_type.startswith('video/') else 'audio'
    
    # Create Recording model instance
    recording = Recording.objects.create(
        session=session,
        file=recording_file,
        file_type=file_type
    )
    
    # Trigger transcription asynchronously (in production, use Celery)
    transcribe_recording_async(recording.id)
    
    return JsonResponse({
        'success': True,
        'recording_id': recording.id,
        'message': 'Recording uploaded successfully. Transcription in progress.'
    })


def transcribe_recording_async(recording_id: int) -> None:
    """
    Transcribe a recording using OpenAI Whisper API.
    This should be run asynchronously (e.g., with Celery) in production.
    
    Args:
        recording_id: The ID of the Recording model instance to transcribe
    """
    import threading
    from analysis.models import Recording
    
    def transcribe() -> None:
        """Internal function to perform transcription."""
        try:
            recording = Recording.objects.get(id=recording_id)
            
            # Check if API key is available
            if not settings.OPENAI_API_KEY:
                recording.transcription = "Error: OpenAI API key not configured"
                recording.save()
                return
            
            # Check if file exists
            if not recording.file:
                recording.transcription = "Error: No file attached to recording"
                recording.save()
                return
            
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Open the file and transcribe
            with recording.file.open('rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            # Save transcription
            recording.transcription = transcript
            recording.save()
            
        except Recording.DoesNotExist:
            # Recording was deleted before transcription could complete
            pass
        except Exception as e:
            # Handle errors gracefully
            try:
                recording = Recording.objects.get(id=recording_id)
                recording.transcription = f"Error transcribing: {str(e)}"
                recording.save()
            except Recording.DoesNotExist:
                pass
    
    # Run in background thread (in production, use Celery)
    thread = threading.Thread(target=transcribe)
    thread.daemon = True
    thread.start()

