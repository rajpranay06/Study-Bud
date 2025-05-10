# Converts any response to JSON

from rest_framework.serializers import ModelSerializer
from base.models import Room, User, Topic, Message, Poll, PollOption, EmojiReaction, RoomJoinRequest
from rest_framework import serializers

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'bio', 'avatar']

class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class MessageSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'

class PollOptionSerializer(ModelSerializer):
    vote_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PollOption
        fields = ['id', 'option_text', 'vote_count']

class PollSerializer(ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Poll
        fields = '__all__'

class EmojiReactionSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EmojiReaction
        fields = '__all__'

class RoomJoinRequestSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    
    class Meta:
        model = RoomJoinRequest
        fields = '__all__'

class RoomSerializer(ModelSerializer):
    host = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'
        