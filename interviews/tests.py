"""
Tests for interviews app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import InterviewSession, Message
from cases.models import Case

User = get_user_model()


class InterviewSessionModelTest(TestCase):
    """Test cases for InterviewSession model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_interview_session(self):
        """Test creating an interview session."""
        session = InterviewSession.objects.create(
            user=self.user,
            mode=InterviewSession.INTERVIEWER_LED
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.mode, InterviewSession.INTERVIEWER_LED)
        self.assertEqual(session.status, 'not_started')
    
    def test_create_message(self):
        """Test creating a message in a session."""
        session = InterviewSession.objects.create(
            user=self.user,
            mode=InterviewSession.INTERVIEWER_LED
        )
        message = Message.objects.create(
            session=session,
            role='user',
            content='Test message'
        )
        self.assertEqual(message.session, session)
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Test message')


class InterviewViewsTest(TestCase):
    """Test cases for interview views."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test case
        self.case = Case.objects.create(
            title='Test Case',
            case_type='consulting',
            prompt='Test prompt',
            context={'client': 'Test Client'},
            exhibits=[]
        )
    
    def test_interview_list_view(self):
        """Test interview list view."""
        response = self.client.get('/interviews/')
        self.assertEqual(response.status_code, 200)
    
    def test_interview_start_view_get(self):
        """Test interview start view (GET)."""
        response = self.client.get('/interviews/start/')
        self.assertEqual(response.status_code, 200)
    
    def test_interview_start_view_post(self):
        """Test interview start view (POST)."""
        response = self.client.post('/interviews/start/', {
            'case_id': self.case.id,
            'mode': InterviewSession.INTERVIEWER_LED
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(InterviewSession.objects.filter(user=self.user).exists())
    
    def test_interview_detail_view(self):
        """Test interview detail view."""
        session = InterviewSession.objects.create(
            user=self.user,
            case=self.case,
            mode=InterviewSession.INTERVIEWER_LED,
            status='in_progress'
        )
        response = self.client.get(f'/interviews/{session.id}/')
        self.assertEqual(response.status_code, 200)
    
    @patch('interviews.views.EvaluatorAgent')
    @patch('interviews.views.CoachAgent')
    def test_evaluate_interview_view(self, mock_coach, mock_evaluator):
        """Test interview evaluation view."""
        from analysis.models import Evaluation
        from feedback.models import Feedback
        
        session = InterviewSession.objects.create(
            user=self.user,
            case=self.case,
            mode=InterviewSession.INTERVIEWER_LED,
            status='completed'
        )
        
        # Mock evaluator
        mock_eval_instance = mock_evaluator.return_value
        mock_eval_instance.evaluate_interview.return_value = {
            'structure_score': 80,
            'hypothesis_score': 75,
            'math_score': 90,
            'insights_score': 85,
            'overall_score': 82,
            'strengths': ['Good structure'],
            'areas_for_improvement': ['More data']
        }
        
        # Mock coach
        mock_coach_instance = mock_coach.return_value
        mock_coach_instance.generate_feedback.return_value = {
            'summary': 'Good performance',
            'strengths': ['Good structure'],
            'areas_for_improvement': ['More data'],
            'recommendations': ['Practice more']
        }
        
        response = self.client.post(f'/interviews/{session.id}/evaluate/')
        self.assertEqual(response.status_code, 302)  # Redirect to feedback
        
        # Check that evaluation was created
        self.assertTrue(Evaluation.objects.filter(session=session).exists())
    
    @patch('interviews.views.transcribe_recording_async')
    def test_upload_recording_view(self, mock_transcribe):
        """Test recording upload view."""
        session = InterviewSession.objects.create(
            user=self.user,
            case=self.case,
            mode=InterviewSession.INTERVIEWER_LED
        )
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_recording.webm",
            b"fake video content",
            content_type="video/webm"
        )
        
        response = self.client.post(
            f'/interviews/{session.id}/upload-recording/',
            {'recording': test_file, 'session_id': session.id}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        mock_transcribe.assert_called_once()

