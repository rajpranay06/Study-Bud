from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from base.models import Room, Topic

User = get_user_model()

class LandingPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create test topic
        self.topic = Topic.objects.create(name='Python')
        
        # Create test rooms
        self.room1 = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room 1',
            description='A room for testing purposes',
            is_private=False
        )
        
        self.room2 = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name='Test Room 2',
            description='Another room for testing',
            is_private=True
        )
    
    def test_landing_page_unauthenticated(self):
        """Test landing page is shown to unauthenticated users"""
        response = self.client.get(reverse('home'))
        
        # Check that landing page is shown
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/landing_page.html')
        
        # Check that home page is not shown
        self.assertTemplateNotUsed(response, 'base/home.html')
    
    def test_home_page_authenticated(self):
        """Test home page is shown to authenticated users"""
        # Login the user
        self.client.login(email='test@example.com', password='testpassword123')
        
        response = self.client.get(reverse('home'))
        
        # Check that home page is shown
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')
        
        # Check that landing page is not shown
        self.assertTemplateNotUsed(response, 'base/landing_page.html')
        
        # Check that rooms are visible in the context
        self.assertIn('rooms', response.context)
        self.assertEqual(len(response.context['rooms']), 2)
    
    def test_topics_page_unauthenticated(self):
        """Test topics page redirects unauthenticated users to login"""
        response = self.client.get(reverse('topics'))
        
        # Check redirect to login
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={reverse("topics")}')
    
    def test_topics_page_authenticated(self):
        """Test topics page is accessible to authenticated users"""
        # Login the user
        self.client.login(email='test@example.com', password='testpassword123')
        
        response = self.client.get(reverse('topics'))
        
        # Check successful access
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/topics.html')
        
        # Check topics in context
        self.assertIn('topics', response.context)
        self.assertEqual(len(response.context['topics']), 1)
        self.assertEqual(response.context['topics'][0].name, 'Python')
    
    def test_activity_page_unauthenticated(self):
        """Test activity page redirects unauthenticated users to login"""
        response = self.client.get(reverse('activity'))
        
        # Check redirect to login
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={reverse("activity")}')
    
    def test_activity_page_authenticated(self):
        """Test activity page is accessible to authenticated users"""
        # Login the user
        self.client.login(email='test@example.com', password='testpassword123')
        
        response = self.client.get(reverse('activity'))
        
        # Check successful access
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/activity.html')
    
    def test_register_page(self):
        """Test register page is accessible"""
        response = self.client.get(reverse('register'))
        
        # Check successful access
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')
    
    def test_login_page(self):
        """Test login page is accessible"""
        response = self.client.get(reverse('login'))
        
        # Check successful access
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')
    
    def test_logout_functionality(self):
        """Test logout functionality"""
        # Login the user
        self.client.login(email='test@example.com', password='testpassword123')
        
        # Confirm user is logged in
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'base/home.html')
        
        # Logout the user
        response = self.client.get(reverse('logout'))
        
        # Check redirect after logout
        self.assertRedirects(response, reverse('home'))
        
        # Confirm landing page is shown after logout
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'base/landing_page.html') 