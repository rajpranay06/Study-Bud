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
        # Login with correct credentials
        login_successful = self.client.login(username='testuser', password='oldpassword123')
        self.assertTrue(login_successful, "Login failed during setup")
        
    def test_password_change_page_load(self):
        """Test password change page loads correctly"""
        response = self.client.get(reverse('change-password-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/change_password.html')
        
    def test_password_change_functionality(self):
        """Test password change works correctly"""
        # Test with valid form data
        response = self.client.post(reverse('change-password'), {
            'old_password': 'oldpassword123',
            'new_password1': 'Newpassword456!',  # Stronger password
            'new_password2': 'Newpassword456!'
        })
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Test new password works with username login
        self.client.logout()
        login_successful = self.client.login(username='testuser', password='Newpassword456!')
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
        initial_user_count = User.objects.count()
        
        # Use a stronger password that meets validation requirements
        response = self.client.post(reverse('register'), {
            'name': 'New User',
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!'
        }, follow=True)  # Follow redirects
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Test that the user was created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        self.assertTrue(User.objects.filter(username='newuser').exists()) 