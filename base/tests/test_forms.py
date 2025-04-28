from django.test import TestCase
from django.contrib.auth import get_user_model
from base.models import Topic
from base.forms import MyUserCreationForm, RoomForm

User = get_user_model()

class FormTests(TestCase):
    def test_user_creation_form_valid(self):
        """Test valid user creation form"""
        form_data = {
            'name': 'Test User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        form = MyUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_user_creation_form_invalid(self):
        """Test invalid user creation form with mismatched passwords"""
        form_data = {
            'name': 'Test User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'wrongpassword'
        }
        form = MyUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_room_form_valid(self):
        """Test valid room creation form"""
        topic = Topic.objects.create(name='Testing')
        
        form_data = {
            'topic': topic.id,
            'name': 'Test Room',
            'description': 'A room for testing purposes',
            'is_private': False,
            'welcome_message': 'Welcome {user} to {room}!'
        }
        
        form = RoomForm(data=form_data)
        self.assertTrue(form.is_valid()) 