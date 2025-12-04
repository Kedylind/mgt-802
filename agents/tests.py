"""
Tests for agents app.
"""
from django.test import TestCase
from unittest.mock import patch, MagicMock
from agents.case_generator import CaseGenerator
from agents.interviewer import InterviewerAgent
from agents.evaluator import EvaluatorAgent
from agents.coach import CoachAgent


class CaseGeneratorTest(TestCase):
    """Test cases for CaseGenerator agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = CaseGenerator()
    
    @patch('agents.case_generator.Crew')
    def test_generate_case(self, mock_crew):
        """Test case generation."""
        # Mock crew response
        mock_result = MagicMock()
        mock_result.raw = '{"title": "Test Case", "prompt": "Test prompt", "context": {}, "exhibits": []}'
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew.return_value = mock_crew_instance
        
        # Test case generation
        result = self.generator.generate_case("Test Topic", "consulting")
        
        self.assertIn("title", result)
        self.assertIn("prompt", result)
    
    def test_generate_case_error_handling(self):
        """Test error handling in case generation."""
        with patch('agents.case_generator.Crew') as mock_crew:
            mock_crew_instance = MagicMock()
            mock_crew_instance.kickoff.side_effect = Exception("Test error")
            mock_crew.return_value = mock_crew_instance
            
            result = self.generator.generate_case("Test Topic", "consulting")
            self.assertIn("Error Generating Case", result["title"])


class InterviewerAgentTest(TestCase):
    """Test cases for InterviewerAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.case_data = {
            "title": "Test Case",
            "prompt": "Test prompt",
            "context": {"client": "Test Client"},
            "exhibits": [
                {"title": "Exhibit 1", "type": "table", "data": {"key": "value"}}
            ],
            "case_type": "consulting"
        }
        self.interviewer = InterviewerAgent(self.case_data, "interviewer_led")
    
    def test_get_opening_message(self):
        """Test opening message generation."""
        message = self.interviewer.get_opening_message()
        self.assertIn("Welcome", message)
        self.assertIn("Test prompt", message)
    
    def test_is_exhibit_request(self):
        """Test exhibit request detection."""
        self.assertTrue(self.interviewer._is_exhibit_request("Can I see the exhibit?"))
        self.assertTrue(self.interviewer._is_exhibit_request("Show me the data"))
        self.assertFalse(self.interviewer._is_exhibit_request("I think the answer is..."))
    
    def test_handle_exhibit_request(self):
        """Test exhibit handling."""
        response = self.interviewer._handle_exhibit_request("Can I see exhibit 1?")
        self.assertIn("Exhibit", response)
        self.assertEqual(len(self.interviewer.exhibits_released), 1)
    
    @patch('agents.interviewer.OpenAI')
    def test_process_candidate_message(self, mock_openai):
        """Test processing candidate messages."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "That's interesting. Can you elaborate?"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        response = self.interviewer.process_candidate_message("I think the solution is X")
        self.assertIsInstance(response, str)
        self.assertEqual(len(self.interviewer.conversation_history), 2)


class EvaluatorAgentTest(TestCase):
    """Test cases for EvaluatorAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = EvaluatorAgent()
    
    @patch('agents.evaluator.OpenAI')
    def test_evaluate_interview(self, mock_openai):
        """Test interview evaluation."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        SCORES:
        Structure: 80
        Hypothesis: 75
        Math: 90
        Insights: 85
        Overall: 82
        
        STRENGTHS:
        - Good structure
        - Clear thinking
        
        AREAS FOR IMPROVEMENT:
        - More data needed
        """
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        case_data = {"title": "Test Case", "case_type": "consulting", "prompt": "Test"}
        conversation = [{"role": "user", "content": "Test response"}]
        
        result = self.evaluator.evaluate_interview(case_data, conversation)
        
        self.assertIn("structure_score", result)
        self.assertIn("overall_score", result)
        self.assertIn("strengths", result)
    
    def test_parse_evaluation(self):
        """Test evaluation parsing."""
        evaluation_text = """
        SCORES:
        Structure: 80
        Hypothesis: 75
        Math: 90
        Insights: 85
        Overall: 82
        
        STRENGTHS:
        - Good structure
        
        AREAS FOR IMPROVEMENT:
        - More data needed
        """
        
        scores = self.evaluator._parse_evaluation(evaluation_text)
        self.assertEqual(scores["structure"], 80)
        self.assertEqual(scores["overall"], 82)
        self.assertIn("Good structure", scores["strengths"])


class CoachAgentTest(TestCase):
    """Test cases for CoachAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.coach = CoachAgent()
    
    @patch('agents.coach.OpenAI')
    def test_generate_feedback(self, mock_openai):
        """Test feedback generation."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        SUMMARY:
        Good performance overall.
        
        RECOMMENDED DRILLS:
        - Practice math drills
        - Framework exercises
        
        NEXT STEPS:
        - Review case studies
        """
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        evaluation_data = {
            "structure_score": 80,
            "hypothesis_score": 75,
            "math_score": 90,
            "insights_score": 85,
            "overall_score": 82,
            "strengths": ["Good structure"],
            "areas_for_improvement": ["More data"]
        }
        case_data = {"case_type": "consulting"}
        
        result = self.coach.generate_feedback(evaluation_data, case_data)
        
        self.assertIn("summary", result)
        self.assertIn("recommendations", result)
        self.assertIn("next_steps", result)
    
    def test_parse_recommendations(self):
        """Test recommendation parsing."""
        coaching_text = """
        SUMMARY:
        Good performance overall.
        
        RECOMMENDED DRILLS:
        - Practice math drills
        - Framework exercises
        
        NEXT STEPS:
        - Review case studies
        """
        
        recommendations = self.coach._parse_recommendations(coaching_text)
        self.assertIn("Good performance", recommendations["summary"])
        self.assertEqual(len(recommendations["drills"]), 2)
        self.assertEqual(len(recommendations["next_steps"]), 1)
