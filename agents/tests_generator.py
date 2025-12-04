from django.test import TestCase
from unittest.mock import patch, MagicMock
from agents.case_generator import CaseGenerator

class CaseGeneratorTests(TestCase):
    @patch('agents.case_generator.Crew')
    def test_generate_case_success(self, mock_crew_class):
        # Setup mock
        mock_crew_instance = MagicMock()
        mock_crew_class.return_value = mock_crew_instance
        
        mock_result = MagicMock()
        mock_result.raw = '''
        {
            "title": "Test Case",
            "case_type": "consulting",
            "prompt": "Test Prompt",
            "context": {"situation": "test"},
            "exhibits": []
        }
        '''
        mock_crew_instance.kickoff.return_value = mock_result
        
        # Execute
        generator = CaseGenerator()
        result = generator.generate_case("Test Topic")
        
        # Verify
        self.assertEqual(result['title'], "Test Case")
        self.assertEqual(result['case_type'], "consulting")
        self.assertEqual(result['prompt'], "Test Prompt")
