from django.test import TestCase
from django.contrib.auth import get_user_model
from base.models import Room, Topic, Message, Poll, PollOption, RoomJoinRequest

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
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
        
        # Create test message
        self.message = Message.objects.create(
            user=self.user,
            room=self.room,
            body='This is a test message'
        )
        
    def test_user_creation(self):
        """Test user can be created with proper attributes"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpassword123'))
        
    def test_topic_creation(self):
        """Test topic is created correctly"""
        self.assertEqual(str(self.topic), 'Testing')
        
    def test_room_creation(self):
        """Test room is created correctly"""
        self.assertEqual(str(self.room), 'Test Room')
        self.assertEqual(self.room.host, self.user)
        self.assertEqual(self.room.topic, self.topic)
        self.assertFalse(self.room.is_private)
        
    def test_message_creation(self):
        """Test message is created correctly"""
        self.assertEqual(self.message.body, 'This is a test message')
        self.assertEqual(self.message.user, self.user)
        self.assertEqual(self.message.room, self.room)
        
    def test_room_participants(self):
        """Test participants can be added to room"""
        user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com', 
            password='testpass2'
        )
        
        self.room.participants.add(self.user)
        self.room.participants.add(user2)
        
        self.assertEqual(self.room.participants.count(), 2)
        self.assertIn(self.user, self.room.participants.all())
        self.assertIn(user2, self.room.participants.all())
        
    def test_poll_creation(self):
        """Test poll can be created with options"""
        poll = Poll.objects.create(
            room=self.room,
            question='What is your favorite color?',
            created_by=self.user
        )
        
        option1 = PollOption.objects.create(
            poll=poll,
            option_text='Blue'
        )
        
        option2 = PollOption.objects.create(
            poll=poll,
            option_text='Red'
        )
        
        self.assertEqual(poll.options.count(), 2)
        self.assertEqual(str(poll), 'What is your favorite color?')
        
    def test_room_join_request(self):
        """Test join request for private rooms"""
        user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com', 
            password='testpass2'
        )
        
        join_request = RoomJoinRequest.objects.create(
            room=self.room,
            user=user2,
            status='pending'
        )
        
        self.assertEqual(join_request.status, 'pending')
        self.assertEqual(join_request.room, self.room)
        self.assertEqual(join_request.user, user2) 