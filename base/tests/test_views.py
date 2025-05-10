from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from base.models import Room, Topic

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
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
    
    def test_home_view_not_authenticated(self):
        """Test home view renders landing page for non-authenticated users"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/landing_page.html')
    
    def test_home_view_authenticated(self):
        """Test home view renders home page for authenticated users"""
        self.client.login(email='test@example.com', password='testpassword123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')
    
    def test_login_view(self):
        """Test login view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')
        
    def test_login_functionality(self):
        """Test login functionality works"""
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
    def test_room_view_not_authenticated(self):
        """Test room view redirects to login for non-authenticated users"""
        response = self.client.get(reverse('room', kwargs={'pk': self.room.id}))
        self.assertRedirects(response, f"/login/?next=/room_page/{self.room.id}/")
        
    def test_room_view_authenticated(self):
        """Test room view renders for authenticated users"""
        self.client.login(email='test@example.com', password='testpassword123')
        response = self.client.get(reverse('room', kwargs={'pk': self.room.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/room.html')
        
    def test_create_room(self):
        """Test room creation"""
        self.client.login(email='test@example.com', password='testpassword123')
        
        response = self.client.post(reverse('create-room'), {
            'topic': self.topic.id,
            'name': 'New Test Room',
            'description': 'A new room for testing',
            'is_private': False,
            'welcome_message': 'Welcome {user} to {room}!'
        })
        
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Room.objects.filter(name='New Test Room').exists())
        
    def test_update_user(self):
        """Test user profile update"""
        self.client.login(email='test@example.com', password='testpassword123')
        
        response = self.client.post(reverse('update-user'), {
            'name': 'Updated Name',
            'username': 'testuser',
            'email': 'test@example.com',
            'bio': 'This is an updated bio'
        })
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated Name')
        self.assertEqual(self.user.bio, 'This is an updated bio') 