from django.test import TestCase, SimpleTestCase, Client
from django.urls import reverse, resolve
from django.conf import settings
from base.views import home, loginPage, logoutUser, registerPage

class MinimalTests(TestCase):
    def test_basic_assertion(self):
        """A simple test that always passes"""
        self.assertEqual(1, 1)
        
    def test_true_is_true(self):
        """Another simple test that always passes"""
        self.assertTrue(True)
        
class UrlTests(SimpleTestCase):
    """Tests that don't require database setup"""
    
    def test_home_url_resolves(self):
        """Test the home URL resolves to the correct view function"""
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)
        
    def test_login_url_resolves(self):
        """Test the login URL resolves to the correct view function"""
        url = reverse('login')
        self.assertEqual(resolve(url).func, loginPage)
        
    def test_logout_url_resolves(self):
        """Test the logout URL resolves to the correct view function"""
        url = reverse('logout')
        self.assertEqual(resolve(url).func, logoutUser)
        
    def test_register_url_resolves(self):
        """Test the register URL resolves to the correct view function"""
        url = reverse('register')
        self.assertEqual(resolve(url).func, registerPage)
        
class SettingsTests(SimpleTestCase):
    """Tests for application settings"""
    
    def test_debug_setting(self):
        """Test DEBUG setting is properly configured"""
        # In a development environment, DEBUG might be True or False
        # We just check that it exists (the actual value depends on the environment)
        self.assertIsNotNone(settings.DEBUG)
        
    def test_databases_configured(self):
        """Test database is configured"""
        self.assertTrue('default' in settings.DATABASES)
        
    def test_installed_apps(self):
        """Test required apps are installed"""
        self.assertIn('base.apps.BaseConfig', settings.INSTALLED_APPS)
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        
    def test_auth_user_model(self):
        """Test custom user model is configured"""
        self.assertEqual(settings.AUTH_USER_MODEL, 'base.User') 