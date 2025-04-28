from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordChangeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        self.client.login(email='test@example.com', password='oldpassword123')
        
    def test_password_change_page_load(self):
        """Test password change page loads correctly"""
        response = self.client.get(reverse('change-password-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/change_password.html')
        
    def test_password_change_functionality(self):
        """Test password change works correctly"""
        response = self.client.post(reverse('change-password'), {
            'old_password': 'oldpassword123',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456'
        })
        
        self.assertRedirects(response, reverse('update-user'))
        
        # Test new password works
        self.client.logout()
        login_successful = self.client.login(email='test@example.com', password='newpassword456')
        self.assertTrue(login_successful)
        
class RegisterTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_register_page_load(self):
        """Test register page loads correctly"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')
        
    def test_user_registration(self):
        """Test user registration functionality"""
        response = self.client.post(reverse('register'), {
            'name': 'New User',
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        })
        
        # Test that the user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        
        # Test user is logged in after registration
        self.assertRedirects(response, reverse('home')) 