from django.test import SimpleTestCase, Client
from django.urls import reverse

class SimpleViewTests(SimpleTestCase):
    """Test views without database interactions"""
    
    def setUp(self):
        self.client = Client()
    
    def test_login_view_get(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')
    
    def test_register_view_get(self):
        """Test register page loads correctly"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')
    
    def test_landing_page_get(self):
        """Test landing page loads for anonymous users"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/landing_page.html')
    
    def test_login_required_views(self):
        """Test views that require login redirect to login page"""
        # Test profile page requires login
        response = self.client.get(reverse('update-user'))
        self.assertEqual(response.status_code, 302)  # 302 = redirect
        self.assertTrue(response.url.startswith('/login/'))
        
        # Test topics page requires login
        response = self.client.get(reverse('topics'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
        
        # Test activity page requires login
        response = self.client.get(reverse('activity'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
    
    def test_invalid_room_access(self):
        """Test accessing invalid room ID returns appropriate error"""
        response = self.client.get(reverse('room', kwargs={'pk': 99999}))
        # Should redirect to login page first
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/')) 