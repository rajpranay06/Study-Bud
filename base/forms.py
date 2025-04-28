from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Enter a valid email address.'
    )
    
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        
        # Add help text for username
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        
        # Add classes for styling
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with that email already exists.')
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password, self.instance)
        except ValidationError as error:
            self.add_error('password1', error)
        return password

class RoomForm(ModelForm):
    class Meta:  #MetaData
        model = Room
        fields = ['topic', 'name', 'description', 'is_private', 'welcome_message']
        exclude = ['host', 'participants']
        
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        
        # Add classes for styling and better labels
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
        
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'