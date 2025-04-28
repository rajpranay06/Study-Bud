from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from base.models import Room, Topic

User = get_user_model()

class GroqAPITests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create test topic
        self.topic = Topic.objects.create(name='Python')
        
        # Create test room
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room',
            description='A room for testing purposes',
            is_private=False
        )
        
        # Log in the user
        self.client.login(email='test@example.com', password='testpassword123')
    
    @patch('base.views.client')
    def test_generate_quiz(self, mock_client):
        """Test generating a quiz with mocked GROQ response"""
        # Create a mock response for the GROQ completion
        mock_message = MagicMock()
        mock_message.content = """```json
        {
            "title": "Python Basics Quiz",
            "questions": [
                {
                    "question": "What is Python?",
                    "options": ["A snake", "A programming language", "A game", "A movie"],
                    "correctAnswer": "B",
                    "explanation": "Python is a programming language."
                }
            ],
            "recommendedTimeInMinutes": 5
        }
        ```"""
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        
        # Set up the mock client to return our mock completion
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Call the view to generate a quiz
        response = self.client.post(
            reverse('generate-quiz', kwargs={'pk': self.room.id}),
            {'topic': 'Python', 'difficulty': 'easy', 'num_questions': 5}
        )
        
        # Assert the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify the mock was called with expected parameters
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('base.views.client')
    def test_generate_quiz_api(self, mock_client):
        """Test the quiz generation API endpoint"""
        # Create a mock response
        mock_message = MagicMock()
        mock_message.content = """```json
        {
            "title": "Python Basics Quiz",
            "questions": [
                {
                    "question": "What is Python?",
                    "options": ["A snake", "A programming language", "A game", "A movie"],
                    "correctAnswer": "B",
                    "explanation": "Python is a programming language."
                }
            ],
            "recommendedTimeInMinutes": 5
        }
        ```"""
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30
        
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = mock_usage
        
        # Set up the mock client
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Make a request to the API endpoint
        response = self.client.post(
            reverse('generate-quiz', kwargs={'pk': self.room.id}),
            {'topic': 'Python', 'difficulty': 'easy', 'count': 1},
            content_type='application/json'
        )
        
        # Assert the response
        self.assertEqual(response.status_code, 200) 