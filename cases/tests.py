"""
Tests for cases app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Case

User = get_user_model()


class CaseModelTest(TestCase):
    """Test cases for Case model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_case(self):
        """Test creating a case."""
        case = Case.objects.create(
            title='Test Case',
            case_type=Case.CONSULTING,
            prompt='Test prompt',
            context={'industry': 'tech'},
            exhibits=[]
        )
        self.assertEqual(case.title, 'Test Case')
        self.assertEqual(case.case_type, Case.CONSULTING)

