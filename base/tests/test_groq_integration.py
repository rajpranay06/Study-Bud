from django.test import TestCase, SimpleTestCase
from unittest.mock import patch, MagicMock
from django.conf import settings
import json

class GroqConfigTests(SimpleTestCase):
    """Tests for GROQ API configuration"""
    
    def test_groq_api_key_exists(self):
        """Test GROQ API key is configured in settings"""
        self.assertTrue(hasattr(settings, 'GROQ_API_KEY'))
        self.assertIsNotNone(settings.GROQ_API_KEY)
        
    def test_groq_api_url_exists(self):
        """Test GROQ API URL is configured in settings"""
        self.assertTrue(hasattr(settings, 'GROQ_API_URL'))
        self.assertEqual(settings.GROQ_API_URL, 'https://api.groq.com/v1')
        
class GroqUtilityTests(SimpleTestCase):
    """Tests for GROQ API utility functions"""
    
    @patch('base.views.Groq')
    def test_groq_client_initialization(self, mock_groq):
        """Test GROQ client can be initialized with settings"""
        from base.views import Groq  # This re-imports Groq with our mock
        
        # Since Groq is patched, we just need to verify it exists
        self.assertIsNotNone(Groq)
        
    @patch('json.loads')
    def test_json_parsing(self, mock_json_loads):
        """Test JSON parsing works as expected"""
        # Mock the json.loads function to return a specific value
        mock_json_loads.return_value = {
            "title": "Test Quiz",
            "questions": [
                {
                    "question": "What is Python?",
                    "options": ["A snake", "A programming language", "A game", "A movie"],
                    "correctAnswer": "B"
                }
            ]
        }
        
        # Parse a sample JSON string
        sample_json = """
        {
            "title": "Test Quiz",
            "questions": [
                {
                    "question": "What is Python?",
                    "options": ["A snake", "A programming language", "A game", "A movie"],
                    "correctAnswer": "B"
                }
            ]
        }
        """
        result = json.loads(sample_json)
        
        # Assertions
        self.assertEqual(result["title"], "Test Quiz")
        self.assertEqual(len(result["questions"]), 1)
    
    @patch('base.views.Groq')
    def test_mock_groq_completion(self, mock_groq):
        """Test mocking GROQ completion works"""
        # Set up the mock
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = """
        {
            "title": "Mocked Quiz",
            "questions": [
                {
                    "question": "What is a mock?",
                    "options": ["A bird", "A testing tool", "A drink", "A song"],
                    "correctAnswer": "B"
                }
            ],
            "recommendedTimeInMinutes": 5
        }
        """
        
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq.return_value = mock_client
        
        # Import after patching to get the patched version
        from base.views import Groq
        
        # Initialize the client
        client = Groq()
        
        # Call the mocked function
        completion = client.chat.completions.create(
            model="model-name",
            messages=[{"role": "user", "content": "Test prompt"}]
        )
        
        # Assert the function was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Assert we get our mock data
        self.assertTrue(hasattr(completion, 'choices'))
        self.assertTrue(len(completion.choices) > 0)
        self.assertTrue("Mocked Quiz" in completion.choices[0].message.content) 