from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db.models import Q
from groq import Groq
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json

from base.models import Room, User, Topic, Message, Poll, PollOption, EmojiReaction, RoomJoinRequest
from .serializers import (
    RoomSerializer, 
    UserSerializer, 
    TopicSerializer, 
    MessageSerializer,
    PollSerializer,
    PollOptionSerializer,
    EmojiReactionSerializer,
    RoomJoinRequestSerializer
)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id',
        'GET /api/topics',
        'GET /api/users',
        'GET /api/users/:id',
        'GET /api/rooms/:id/messages',
        'GET /api/rooms/:id/polls',
        'POST /api/groq-chat',
        'POST /api/generate-quiz',
        'POST /api/rooms/:id/generate-quiz',
        'POST /api/rooms',
        'PUT /api/rooms/:id',
        'DELETE /api/rooms/:id',
        'POST /api/rooms/:id/join-request',
        'GET /api/rooms/:id/join-requests',
        'PUT /api/join-requests/:id',
        'POST /api/polls/:id/vote/:option_id',
        'POST /api/messages/:id/react'
    ]
    return Response(routes)

# Room endpoints
@swagger_auto_schema(
    methods=['get'],
    operation_description="Get a list of all rooms",
    responses={200: RoomSerializer(many=True)}
)
@api_view(['GET'])
def getRooms(request):
    """
    Get a list of all rooms
    """
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    methods=['get'],
    operation_description="Get details of a specific room",
    responses={200: RoomSerializer(), 404: "Room not found"}
)
@api_view(['GET'])
def getRoom(request, pk):
    """
    Get details of a specific room
    """
    try:
        room = Room.objects.get(id=pk)
        serializer = RoomSerializer(room, many=False)
        return Response(serializer.data)
    except Room.DoesNotExist:
        return Response({"error": f"Room with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

# Topic endpoints
@swagger_auto_schema(
    methods=['get'],
    operation_description="Get a list of all topics",
    responses={200: TopicSerializer(many=True)}
)
@api_view(['GET'])
def getTopics(request):
    """
    Get a list of all topics
    """
    topics = Topic.objects.all()
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data)

# User endpoints
@swagger_auto_schema(
    methods=['get'],
    operation_description="Get a list of all users",
    responses={200: UserSerializer(many=True)}
)
@api_view(['GET'])
def getUsers(request):
    """
    Get a list of all users
    """
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    methods=['get'],
    operation_description="Get details of a specific user",
    responses={200: UserSerializer(), 404: "User not found"}
)
@api_view(['GET'])
def getUser(request, pk):
    """
    Get details of a specific user
    """
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({"error": f"User with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

# Message endpoints
@swagger_auto_schema(
    methods=['get'],
    operation_description="Get messages for a specific room",
    responses={200: MessageSerializer(many=True), 404: "Room not found"}
)
@api_view(['GET'])
def getRoomMessages(request, pk):
    """
    Get all messages for a specific room
    """
    try:
        room = Room.objects.get(id=pk)
        messages = room.message_set.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Room.DoesNotExist:
        return Response({"error": f"Room with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

# Poll endpoints
@swagger_auto_schema(
    methods=['get'],
    operation_description="Get polls for a specific room",
    responses={200: PollSerializer(many=True), 404: "Room not found"}
)
@api_view(['GET'])
def getRoomPolls(request, pk):
    """
    Get all polls for a specific room
    """
    try:
        room = Room.objects.get(id=pk)
        polls = room.poll_set.all()
        serializer = PollSerializer(polls, many=True)
        return Response(serializer.data)
    except Room.DoesNotExist:
        return Response({"error": f"Room with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

# Poll voting endpoint
poll_vote_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={},
    required=[]
)

@swagger_auto_schema(
    methods=['post'],
    operation_description="Vote on a poll option",
    request_body=poll_vote_schema,
    responses={200: "Vote recorded", 400: "Bad request", 404: "Poll or option not found"}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def votePoll(request, poll_id, option_id):
    """
    Vote on a poll option
    """
    try:
        poll = Poll.objects.get(id=poll_id)
        option = PollOption.objects.get(id=option_id, poll=poll)
        
        # Remove user from all other options in this poll
        for other_option in poll.options.all():
            other_option.votes.remove(request.user)
            
        # Add user's vote to the selected option
        option.votes.add(request.user)
        
        serializer = PollSerializer(poll)
        return Response(serializer.data)
    except Poll.DoesNotExist:
        return Response({"error": f"Poll with id {poll_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    except PollOption.DoesNotExist:
        return Response({"error": f"Option with id {option_id} not found for poll {poll_id}"}, status=status.HTTP_404_NOT_FOUND)

# Room CRUD operations
room_create_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Room name'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Room description'),
        'topic_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Topic ID'),
        'is_private': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the room is private'),
    },
    required=['name', 'topic_id']
)

@swagger_auto_schema(
    methods=['post'],
    operation_description="Create a new room",
    request_body=room_create_schema,
    responses={201: RoomSerializer(), 400: "Bad request"}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createRoom(request):
    """
    Create a new room
    """
    try:
        data = request.data
        topic_id = data.get('topic_id')
        
        if not topic_id:
            return Response({"error": "Topic ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({"error": f"Topic with id {topic_id} not found"}, status=status.HTTP_404_NOT_FOUND)
            
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=data.get('name'),
            description=data.get('description', ''),
            is_private=data.get('is_private', False)
        )
        
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['put'],
    operation_description="Update a room",
    request_body=room_create_schema,
    responses={200: RoomSerializer(), 400: "Bad request", 403: "Not authorized", 404: "Room not found"}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateRoom(request, pk):
    """
    Update a room (only available to the room host)
    """
    try:
        room = Room.objects.get(id=pk)
        
        # Check if user is the host
        if request.user != room.host:
            return Response({"error": "You are not authorized to update this room"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        
        # Update room fields
        if 'name' in data:
            room.name = data['name']
        if 'description' in data:
            room.description = data['description']
        if 'is_private' in data:
            room.is_private = data['is_private']
        if 'topic_id' in data:
            try:
                topic = Topic.objects.get(id=data['topic_id'])
                room.topic = topic
            except Topic.DoesNotExist:
                return Response({"error": f"Topic with id {data['topic_id']} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        room.save()
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    except Room.DoesNotExist:
        return Response({"error": f"Room with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['delete'],
    operation_description="Delete a room",
    responses={204: "Room deleted", 403: "Not authorized", 404: "Room not found"}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteRoom(request, pk):
    """
    Delete a room (only available to the room host)
    """
    try:
        room = Room.objects.get(id=pk)
        
        # Check if user is the host
        if request.user != room.host:
            return Response({"error": "You are not authorized to delete this room"}, status=status.HTTP_403_FORBIDDEN)
        
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Room.DoesNotExist:
        return Response({"error": f"Room with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

# Join request endpoints
join_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={},
    required=[]
)

@swagger_auto_schema(
    methods=['post'],
    operation_description="Request to join a private room",
    request_body=join_request_schema,
    responses={201: RoomJoinRequestSerializer(), 400: "Bad request", 404: "Room not found"}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createJoinRequest(request, pk):
    """
    Request to join a private room
    """
    try:
        room = Room.objects.get(id=pk)
        
        # Check if room is private
        if not room.is_private:
            return Response({"error": "This is not a private room"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if user is already a participant
        if request.user == room.host or request.user in room.participants.all():
            return Response({"error": "You are already a member of this room"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if request already exists
        existing_request = RoomJoinRequest.objects.filter(room=room, user=request.user).first()
        if existing_request:
            if existing_request.status == 'pending':
                return Response({"error": "You already have a pending request for this room"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Update status to pending
                existing_request.status = 'pending'
                existing_request.save()
                serializer = RoomJoinRequestSerializer(existing_request)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new request
        join_request = RoomJoinRequest.objects.create(
            room=room,
            user=request.user,
            status='pending'
        )
        
        serializer = RoomJoinRequestSerializer(join_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Room.DoesNotExist:
        return Response({"error": f"Room with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    methods=['get'],
    operation_description="Get join requests for a room",
    responses={200: RoomJoinRequestSerializer(many=True), 403: "Not authorized", 404: "Room not found"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRoomJoinRequests(request, pk):
    """
    Get join requests for a room (only available to the room host)
    """
    try:
        room = Room.objects.get(id=pk)
        
        # Check if user is the host
        if request.user != room.host:
            return Response({"error": "You are not authorized to view join requests for this room"}, status=status.HTTP_403_FORBIDDEN)
            
        join_requests = room.join_requests.all()
        serializer = RoomJoinRequestSerializer(join_requests, many=True)
        return Response(serializer.data)
    except Room.DoesNotExist:
        return Response({"error": f"Room with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

join_request_update_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Request status (approved or rejected)'),
    },
    required=['status']
)

@swagger_auto_schema(
    methods=['put'],
    operation_description="Process a join request",
    request_body=join_request_update_schema,
    responses={200: RoomJoinRequestSerializer(), 400: "Bad request", 403: "Not authorized", 404: "Join request not found"}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def processJoinRequest(request, pk):
    """
    Process a join request (only available to the room host)
    """
    try:
        join_request = RoomJoinRequest.objects.get(id=pk)
        
        # Check if user is the host
        if request.user != join_request.room.host:
            return Response({"error": "You are not authorized to process join requests for this room"}, status=status.HTTP_403_FORBIDDEN)
            
        data = request.data
        status_value = data.get('status')
        
        if status_value not in ['approved', 'rejected']:
            return Response({"error": "Status must be either 'approved' or 'rejected'"}, status=status.HTTP_400_BAD_REQUEST)
            
        join_request.status = status_value
        join_request.save()
        
        # If approved, add user to room participants
        if status_value == 'approved':
            join_request.room.participants.add(join_request.user)
            
        serializer = RoomJoinRequestSerializer(join_request)
        return Response(serializer.data)
    except RoomJoinRequest.DoesNotExist:
        return Response({"error": f"Join request with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

# Emoji reaction endpoint
emoji_reaction_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'emoji': openapi.Schema(type=openapi.TYPE_STRING, description='Emoji code'),
    },
    required=['emoji']
)

@swagger_auto_schema(
    methods=['post'],
    operation_description="Add an emoji reaction to a message",
    request_body=emoji_reaction_schema,
    responses={201: EmojiReactionSerializer(), 400: "Bad request", 404: "Message not found"}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addEmojiReaction(request, message_id):
    """
    Add an emoji reaction to a message
    """
    try:
        message = Message.objects.get(id=message_id)
        data = request.data
        emoji = data.get('emoji')
        
        if not emoji:
            return Response({"error": "Emoji is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if reaction already exists
        existing_reaction = EmojiReaction.objects.filter(message=message, user=request.user, emoji=emoji).first()
        if existing_reaction:
            # Remove existing reaction (toggle behavior)
            existing_reaction.delete()
            return Response({"message": f"Reaction {emoji} removed"}, status=status.HTTP_200_OK)
            
        # Create new reaction
        reaction = EmojiReaction.objects.create(
            message=message,
            user=request.user,
            emoji=emoji
        )
        
        serializer = EmojiReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Message.DoesNotExist:
        return Response({"error": f"Message with id {message_id} not found"}, status=status.HTTP_404_NOT_FOUND)

# Initialize GROQ client with API key from settings
try:
    client = Groq(
        api_key=settings.GROQ_API_KEY,
    )
except Exception as e:
    print(f"Warning: Failed to initialize GROQ client: {str(e)}")
    client = None

# Define the request body schema for GROQ chat
groq_chat_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'prompt': openapi.Schema(type=openapi.TYPE_STRING, description='The prompt to send to GROQ AI'),
        'model': openapi.Schema(type=openapi.TYPE_STRING, description='GROQ model to use', default="meta-llama/llama-4-scout-17b-16e-instruct"),
        'max_tokens': openapi.Schema(type=openapi.TYPE_INTEGER, description='Maximum tokens for completion', default=1024),
        'temperature': openapi.Schema(type=openapi.TYPE_NUMBER, description='Temperature for generation', default=1.0),
    },
    required=['prompt']
)

@swagger_auto_schema(
    methods=['post'], 
    request_body=groq_chat_schema, 
    responses={200: "GROQ response successful", 400: "Invalid request", 500: "GROQ API error"}
)
@api_view(['POST'])
def groq_chat(request):
    if client is None:
        return Response(
            {"error": "GROQ API client not initialized. Please check your API key."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    """
    Endpoint to interact with GROQ AI.
    """
    try:
        data = request.data
        prompt = data.get('prompt')
        model = data.get('model', "meta-llama/llama-4-scout-17b-16e-instruct")
        max_tokens = data.get('max_tokens', 1024)
        temperature = data.get('temperature', 1.0)
        
        if not prompt:
            return Response({"error": "Prompt is required"}, status=400)
            
        # Create GROQ completion
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        # Extract response content
        response_content = completion.choices[0].message.content
        
        return Response({
            "success": True,
            "response": response_content,
            "model": model,
            "usage": {
                "input_tokens": completion.usage.prompt_tokens,
                "output_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            }
        })
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# Define the request body schema for quiz generation
quiz_generation_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'topic': openapi.Schema(type=openapi.TYPE_STRING, description='Quiz topic'),
        'difficulty': openapi.Schema(type=openapi.TYPE_STRING, description='Quiz difficulty level', default="medium"),
        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of questions', default=5),
        'model': openapi.Schema(type=openapi.TYPE_STRING, description='GROQ model to use', default="meta-llama/llama-4-scout-17b-16e-instruct"),
    },
    required=['topic']
)

@swagger_auto_schema(
    methods=['post'], 
    request_body=quiz_generation_schema, 
    responses={200: "Quiz generated successfully", 400: "Invalid request", 500: "Quiz generation error"}
)
@api_view(['POST'])
def generate_quiz_api(request, pk=None):
    if client is None:
        return Response(
            {"error": "GROQ API client not initialized. Please check your API key."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    """
    Endpoint to generate a quiz using GROQ AI.
    Can be called directly or with a room ID (pk) to associate the quiz with a specific room.
    """
    try:
        data = request.data
        topic = data.get('topic')
        difficulty = data.get('difficulty', 'medium')
        count = data.get('count', 5)
        
        # If room ID is provided, try to get the room details
        room = None
        if pk:
            try:
                room = Room.objects.get(id=pk)
                
                # Check if user is authorized
                if request.user.is_authenticated:
                    if request.user != room.host and request.user not in room.participants.all():
                        return Response({"error": "You must be an approved member of this room to take quizzes"}, status=status.HTTP_403_FORBIDDEN)
                
                # If no topic is specified, use the room's topic
                if not topic and room.topic:
                    topic = room.topic.name
            except Room.DoesNotExist:
                return Response({"error": f"Room with ID {pk} not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not topic:
            return Response({"error": "Topic is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the prompt for quiz generation
        prompt = f"""Generate a timed quiz of {count} multiple-choice questions on the topic "{topic}" with difficulty level {difficulty}.
        
        Format the response as a JSON object with the following structure:
        {{
          "title": "Quiz title",
          "questions": [
            {{
              "question": "Question text",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "correctAnswer": "Correct option letter (A, B, C, or D)",
              "explanation": "Brief explanation of the answer"
            }},
            ... more questions
          ],
          "recommendedTimeInMinutes": recommended time to complete this quiz
        }}
        
        Make sure all questions are factually accurate and each has exactly 4 answer options.
        """
            
        # Create GROQ completion
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_completion_tokens=2048,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        # Extract response content
        response_content = completion.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Look for JSON in code blocks or in the entire response
            json_match = response_content.strip()
            if "```json" in json_match:
                json_match = json_match.split("```json")[1].split("```")[0].strip()
            elif "```" in json_match:
                json_match = json_match.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            quiz_data = json.loads(json_match)
            
            # Validate the quiz data structure
            if "title" not in quiz_data or "questions" not in quiz_data:
                raise ValueError("Invalid quiz data structure")
                
            return Response({
                "success": True,
                "quiz": quiz_data,
                "topic": topic,
                "difficulty": difficulty,
                "count": count
            })
            
        except Exception as json_error:
            # If JSON parsing failed, return the raw response
            return Response({
                "success": False,
                "error": f"Failed to parse quiz data: {str(json_error)}",
                "raw_response": response_content
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)