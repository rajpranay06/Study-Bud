from django.db import models

# Create your models here.
# Where we create our database tables

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True)
    
    avatar = models.ImageField(null=True, default="avatar.svg")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # participants = models.ManyToManyField('User')

    welcome_message = models.TextField(default="Welcome {user} to {room}!")
    is_private = models.BooleanField(default=False)
    
    participants = models.ManyToManyField('User', related_name="participants", blank=True)
    updated = models.DateTimeField(auto_now=True)  # Takes time stamp every time
    created = models.DateTimeField(auto_now_add=True) # Takes time stamp once, when created
    
    # Ordering rooms by updated time stamp
    class Meta:
        ordering = ['-updated', '-created']
        
    def __str__(self):
        return self.name
    
class Message(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    body = models.TextField()
    file = models.FileField(upload_to='message_files/', null=True, blank=True)
    is_image = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated', '-created']
        
    def __str__(self):
        return self.body[:50]
    
    def get_emoji_count(self, emoji_code):
        return self.reactions.filter(emoji=emoji_code).count()
    

class Poll(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class PollOption(models.Model):
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)
    votes = models.ManyToManyField('User', blank=True, related_name="poll_votes")

    def vote_count(self):
        return self.votes.count()

class EmojiReaction(models.Model):
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    emoji = models.CharField(max_length=16)  # Store emoji unicode
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'emoji')

class RoomJoinRequest(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('room', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.room.name} ({self.status})"
