from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from base.models import Room, Topic, Message, Poll, PollOption
from unittest.mock import patch

User = get_user_model()

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create test topic
        self.topic = Topic.objects.create(name='Testing')
        
        # Create test room
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room',
            description='A room for testing purposes',
            is_private=False
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    @patch('base.views.client.chat.completions.create')
    def test_groq_chat_api(self, mock_groq):
        """Test the GROQ chat API endpoint"""
        # Mock the GROQ API response
        mock_response = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': 'This is a test response from GROQ.'
                    })
                })
            ],
            'usage': type('obj', (object,), {
                'prompt_tokens': 10,
                'completion_tokens': 20,
                'total_tokens': 30
            })
        })
        mock_groq.return_value = mock_response
        
        # Test data
        data = {
            'prompt': 'Tell me about Python programming',
            'model': 'meta-llama/llama-4-scout-17b-16e-instruct',
            'max_tokens': 100,
            'temperature': 0.7
        }
        
        # Make the request
        response = self.client.post(reverse('groq-chat'), data, format='json')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('success' in response.data)
        self.assertEqual(response.data['response'], 'This is a test response from GROQ.')
        self.assertEqual(response.data['model'], 'meta-llama/llama-4-scout-17b-16e-instruct')
        
    @patch('base.views.client.chat.completions.create')
    def test_generate_quiz_api(self, mock_groq):
        """Test the quiz generation API endpoint"""
        # Mock quiz data that would be returned
        quiz_data = {
            "title": "Python Programming Quiz",
            "questions": [
                {
                    "question": "What is Python?",
                    "options": ["A snake", "A programming language", "A game", "A movie"],
                    "correctAnswer": "B",
                    "explanation": "Python is a programming language"
                }
            ],
            "recommendedTimeInMinutes": 5
        }
        
        # Mock GROQ API response
        mock_response = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': f'```json\n{str(quiz_data)}\n```'
                    })
                })
            ],
            'usage': type('obj', (object,), {
                'prompt_tokens': 15,
                'completion_tokens': 25,
                'total_tokens': 40
            })
        })
        mock_groq.return_value = mock_response
        
        # Test data
        data = {
            'topic': 'Python',
            'difficulty': 'easy',
            'count': 1
        }
        
        # Make the request
        response = self.client.post(reverse('generate-quiz', kwargs={'pk': self.room.id}), data, format='json')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('success' in response.data)
        self.assertEqual(response.data['topic'], 'Python')
        self.assertEqual(response.data['difficulty'], 'easy')
        
    def test_generate_quiz_no_authentication(self):
        """Test quiz generation without authentication"""
        # Logout to test unauthenticated access
        self.client.force_authenticate(user=None)
        
        data = {
            'topic': 'Python',
            'difficulty': 'easy',
            'count': 1
        }
        
        # Make the request
        response = self.client.post(reverse('generate-quiz', kwargs={'pk': self.room.id}), data, format='json')
        
        # Check that it's unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_generate_quiz_no_topic(self):
        """Test quiz generation with missing topic"""
        data = {
            'difficulty': 'easy',
            'count': 1
        }
        
        # Make the request
        response = self.client.post(reverse('generate-quiz', kwargs={'pk': self.room.id}), data, format='json')
        
        # Check that it requires a topic
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RoomJoinRequestAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.host = User.objects.create_user(
            username='hostuser',
            email='host@example.com',
            password='hostpassword'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create topic
        self.topic = Topic.objects.create(name='Testing')
        
        # Create private room
        self.room = Room.objects.create(
            host=self.host,
            topic=self.topic,
            name='Private Test Room',
            description='A private room for testing',
            is_private=True
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
    
    def test_request_join_room(self):
        """Test requesting to join a private room"""
        response = self.client.post(reverse('request-join-room', kwargs={'pk': self.room.id}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # Redirect after creation
        
        # Check that a join request was created
        self.assertTrue(self.room.join_requests.filter(user=self.user, status='pending').exists())
    
    def test_approve_join_request(self):
        """Test approving a join request"""
        # First create a join request
        self.client.post(reverse('request-join-room', kwargs={'pk': self.room.id}))
        join_request = self.room.join_requests.get(user=self.user)
        
        # Switch to host user to approve the request
        self.client.force_authenticate(user=self.host)
        
        response = self.client.get(reverse('process-join-request', kwargs={
            'request_id': join_request.id,
            'action': 'approve'
        }))
        
        # Refresh from database
        join_request.refresh_from_db()
        
        # Check request was approved
        self.assertEqual(join_request.status, 'approved')
        
        # Check user was added to participants
        self.assertIn(self.user, self.room.participants.all()) 