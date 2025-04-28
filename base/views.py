from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from groq import Groq
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Room, Topic, Message, User, Poll, PollOption, EmojiReaction, RoomJoinRequest
from .forms import RoomForm, UserForm, MyUserCreationForm, CustomPasswordChangeForm
import os
import mimetypes
import json


# Create your views here.
# rooms = [
#     {"id": "1", "name": "Python"},
#     {"id": "2", "name": "Django"},
#     {"id": "3", "name": "JavaScript"},
#     {"id": "4", "name": "React"},
# ]

def loginPage(request):
    
    page = "login"
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        try:
            # Check if the email input is actually an email
            if '@' in email:
                user = User.objects.get(email=email)
            else:
                # If not an email, assume it's a username
                user = User.objects.get(username=email)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'base/login_register.html', {'page': page})
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry based on remember me option
            if not remember_me:
                # Session expires when browser closes
                request.session.set_expiry(0)
            
            # Redirect to the page the user was trying to access, or home
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password is incorrect')
        
    context = {"page": page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form =  MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            # Specify the backend to use for authentication
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed')
            
    context = {"form": form}
    return render(request, 'base/login_register.html', context)

def home(request):
    # Show landing page for non-authenticated users
    if not request.user.is_authenticated:
        return render(request, 'base/landing_page.html')
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    # icontains will get all the topics which have q string in it, i specifies case insensitive
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    # for recent activities, we're getting messages from here
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    context = {"rooms": rooms, "topics": topics, "room_count": room_count, "room_messages": room_messages}
    # Rendering the html page from templates
    return render(request, 'base/home.html', context)


@login_required(login_url="login")
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    polls = Poll.objects.filter(room=room).prefetch_related('options')
    
    # Get join request if exists
    join_request = None
    if request.user.is_authenticated:
        join_request = RoomJoinRequest.objects.filter(
            room=room, 
            user=request.user
        ).first()
    
    # greet user if they just joined and haven't been greeted yet
    if request.user.is_authenticated and request.user in participants:
        # check if ChatBot user exists, or create one
        chatbot_user, created = User.objects.get_or_create(username='ChatBot')

        # avoid duplicate greetings
        already_greeted = room.message_set.filter(
            is_bot=True,
            body__icontains=request.user.username
        ).exists()

        if not already_greeted:
            greeting = room.welcome_message.replace("{user}", request.user.username).replace("{room}", room.name)
            Message.objects.create(
                user=chatbot_user,  
                room=room,
                body=greeting,
                is_bot=True
            )

    # Handle file uploads and message posting
    if request.method == 'POST' and 'body' in request.POST:
        message_body = request.POST.get('body')
        message_file = request.FILES.get('message_file')
        
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = message_body
        )
        
        if message_file:
            message.file = message_file
            # Check if the file is an image
            file_type, _ = mimetypes.guess_type(message_file.name)
            if file_type and file_type.startswith('image'):
                message.is_image = True
            message.save()
            
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    # Get pending request count for room host
    pending_requests_count = 0
    if request.user.is_authenticated and request.user == room.host:
        pending_requests_count = RoomJoinRequest.objects.filter(
            room=room, 
            status='pending'
        ).count()
    
    context = {
        "room": room, 
        "room_messages": room_messages, 
        "participants": participants, 
        'polls': polls,
        'join_request': join_request,
        'pending_requests_count': pending_requests_count
    }
    return render(request, 'base/room.html', context)


@login_required(login_url="login")
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        is_private = 'is_private' in request.POST
        welcome_message = request.POST.get('welcome_message', 'Welcome {user} to {room}!')
        
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get("name"),
            description = request.POST.get('description'),
            is_private = is_private,
            welcome_message = welcome_message
        )
        
        return redirect('home')
        
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)   # To prefill the form with the room information
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Unauthorized to update this room')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.is_private = 'is_private' in request.POST
        room.welcome_message = request.POST.get('welcome_message', 'Welcome {user} to {room}!')
        room.save()
        return redirect('home')
        
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('Unauthorized to update this room')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('Unauthorized to update this room')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
            
    return render(request, 'base/update-user.html', {'form': form})

@login_required(login_url="login")
def changePasswordPage(request):
    form = CustomPasswordChangeForm(request.user)
    context = {'form': form}
    return render(request, 'base/change_password.html', context)

@login_required(login_url="login")
def changePassword(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('update-user')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'base/change_password.html', {'form': form})
            
    return redirect('change-password-page')

@login_required(login_url="login")
def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})


@login_required(login_url="login")
def activityPage(request):
    room_messages = Message.objects.all()[0:5]
    return render(request, 'base/activity.html', {'room_messages': room_messages})


@login_required
def create_poll(request, pk):
    room = Room.objects.get(id=pk)
    
    # Only allow room host or participants to create polls
    if request.user != room.host and request.user not in room.participants.all():
        messages.error(request, "You must be an approved member of this room to create polls")
        return redirect('room', pk=pk)
        
    if request.method == 'POST':
        question = request.POST.get('question')
        options = request.POST.getlist('options')
        
        if len(options) < 2:
            messages.error(request, "Poll must have at least 2 options")
            return redirect('room', pk=pk)
            
        poll = Poll.objects.create(
            room=room,
            question=question,
            created_by=request.user
        )
        
        for option_text in options:
            if option_text.strip():
                PollOption.objects.create(poll=poll, option_text=option_text)
        
        return redirect('room', pk=room.id)
    return redirect('room', pk=pk)

@login_required
def vote_poll(request, poll_id, option_id):
    option = PollOption.objects.get(id=option_id)
    room = option.poll.room
    
    # Check if user is authorized
    if request.user != room.host and request.user not in room.participants.all():
        messages.error(request, "You must be an approved member of this room to vote on polls")
        return redirect('room', pk=room.id)

    for opt in option.poll.options.all():
        opt.votes.remove(request.user)

    # Add new vote
    option.votes.add(request.user)
    return redirect('room', pk=option.poll.room.id)

@login_required
def add_emoji_reaction(request, message_id):
    if request.method == 'POST':
        emoji = request.POST.get('emoji')
        message = Message.objects.get(id=message_id)
        EmojiReaction.objects.get_or_create(
            message=message, 
            user=request.user, 
            emoji=emoji
        )
    return redirect('room', pk=message.room.id)

@login_required
def request_join_room(request, pk):
    room = Room.objects.get(id=pk)
    
    # Don't create a request if user is already a participant or is the host
    if request.user == room.host or request.user in room.participants.all():
        return redirect('room', pk=room.id)
    
    # Create or get the join request
    join_request, created = RoomJoinRequest.objects.get_or_create(
        room=room,
        user=request.user,
        defaults={'status': 'pending'}
    )
    
    # If it wasn't created and was rejected before, set back to pending
    if not created and join_request.status == 'rejected':
        join_request.status = 'pending'
        join_request.save()
        
    messages.success(request, f"Request sent to join {room.name}")
    return redirect('room', pk=room.id)

@login_required
def manage_join_requests(request, pk):
    room = Room.objects.get(id=pk)
    
    # Only room host can view/manage join requests
    if request.user != room.host:
        messages.error(request, "You don't have permission to manage join requests for this room")
        return redirect('room', pk=room.id)
    
    join_requests = RoomJoinRequest.objects.filter(room=room, status='pending')
    
    context = {
        'room': room,
        'join_requests': join_requests
    }
    return render(request, 'base/join_requests.html', context)

@login_required
def process_join_request(request, request_id, action):
    join_request = RoomJoinRequest.objects.get(id=request_id)
    room = join_request.room
    
    # Check if user is the host
    if request.user != room.host:
        messages.error(request, "You don't have permission to process join requests")
        return redirect('room', pk=room.id)
    
    if action == 'approve':
        join_request.status = 'approved'
        join_request.save()
        # Add user to room participants
        room.participants.add(join_request.user)
        messages.success(request, f"Approved {join_request.user.username}'s request to join")
    elif action == 'reject':
        join_request.status = 'rejected'
        join_request.save()
        messages.success(request, f"Rejected {join_request.user.username}'s request to join")
    
    return redirect('manage-join-requests', pk=room.id)

# Initialize GROQ client with API key from settings
api_key = settings.GROQ_API_KEY

# Check if API key exists
if not api_key:
    print("WARNING: GROQ_API_KEY is missing! API features will not work.")
    client = None
else:
    try:
        client = Groq(api_key=api_key)
        print("GROQ client successfully initialized")
    except Exception as e:
        print(f"ERROR initializing GROQ client: {str(e)}")
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

# API - http://127.0.0.1:8000/api/groq-chat/ (POST request)
@swagger_auto_schema(
    method='post', 
    request_body=groq_chat_schema, 
    responses={200: "GROQ response successful", 400: "Invalid request", 500: "GROQ API error"}
)
@api_view(['POST'])
def groq_chat(request):
    """
    Endpoint to interact with GROQ AI.
    """
    try:
        # Check if client is initialized
        if client is None:
            return Response({"error": "GROQ API client not initialized. Please check your API key."}, status=500)
            
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

# API - http://127.0.0.1:8000/api/generate-quiz/ (POST request)
@swagger_auto_schema(
    method='post', 
    request_body=quiz_generation_schema, 
    responses={200: "Quiz generated successfully", 400: "Invalid request", 500: "Quiz generation error"}
)
@api_view(['POST'])
def generate_quiz(request, pk=None):
    """
    Endpoint to generate a quiz using GROQ AI.
    Can be called directly or with a room ID (pk) to associate the quiz with a specific room.
    """
    try:
        # Debug: Print API key (redacted for security)
        api_key = settings.GROQ_API_KEY
        print(f"DEBUG - API key present: {'Yes' if api_key else 'No'}")
        print(f"DEBUG - API key length: {len(api_key) if api_key else 0}")
        
        # Check if client is initialized
        if client is None:
            error_msg = "GROQ API client not initialized. Please check your API key."
            if 'api' in request.path:
                return Response({"error": error_msg}, status=500)
            else:
                messages.error(request, error_msg)
                return redirect('room', pk=pk) if pk else redirect('home')
        
        # Check if this is an API request or a form submission
        is_api_request = request.content_type == 'application/json' or 'api' in request.path
        
        # Handle form data for non-API requests
        if not is_api_request:
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
            count = int(request.POST.get('num_questions', 5))
        else:
            data = request.data
            topic = data.get('topic')
            difficulty = data.get('difficulty', 'medium')
            count = data.get('count', 5)
        
        # If room ID is provided, try to get the room details
        room = None
        if pk:
            try:
                room = Room.objects.get(id=pk)
                
                # Check if user is authorized for non-API requests
                if not is_api_request and request.user.is_authenticated:
                    if request.user != room.host and request.user not in room.participants.all():
                        messages.error(request, "You must be an approved member of this room to take quizzes")
                        return redirect('room', pk=pk)
                
                # If no topic is specified, use the room's topic
                if not topic and room.topic:
                    topic = room.topic.name
            except Room.DoesNotExist:
                if is_api_request:
                    return Response({"error": f"Room with ID {pk} not found"}, status=404)
                else:
                    messages.error(request, f"Room with ID {pk} not found")
                    return redirect('home')
        
        if not topic:
            if is_api_request:
                return Response({"error": "Topic is required"}, status=400)
            else:
                messages.error(request, "Topic is required")
                return redirect('room', pk=pk)
        
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
                
            # Return response based on request type
            if is_api_request:
                return Response({
                    "success": True,
                    "quiz": quiz_data,
                    "topic": topic,
                    "difficulty": difficulty,
                    "count": count
                })
            else:
                # Render the quiz template for form submissions
                context = {
                    "quiz": quiz_data,
                    "topic": topic,
                    "difficulty": difficulty,
                    "room": room
                }
                return render(request, 'base/quiz_results.html', context)
            
        except Exception as json_error:
            # If JSON parsing failed, return the raw response
            if is_api_request:
                return Response({
                    "success": False,
                    "error": f"Failed to parse quiz data: {str(json_error)}",
                    "raw_response": response_content
                }, status=400)
            else:
                messages.error(request, f"Failed to generate quiz: {str(json_error)}")
                return redirect('room', pk=pk)
        
    except Exception as e:
        if is_api_request:
            return Response({"error": str(e)}, status=500)
        else:
            messages.error(request, f"Error generating quiz: {str(e)}")
            return redirect('room', pk=pk)

# Example of the streaming version (for testing in the terminal)
def test_groq_streaming():
    """
    Test function for GROQ AI with streaming.
    This is not exposed via API but can be called for testing.
    """
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": "Create a quiz of 5 questions on harry potter with difficulty level medium\n "
                }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        for chunk in completion:
            print(chunk.choices[0].delta.content or "", end="")
            
    except Exception as e:
        print(f"Error: {str(e)}")

@login_required
def submit_quiz(request, pk):
    """
    Handle quiz submission and display results.
    This is a placeholder as we're already checking answers client-side.
    In a real app, you might want to save scores or provide more functionality.
    """
    room = Room.objects.get(id=pk)
    
    # Check if user is authorized
    if request.user != room.host and request.user not in room.participants.all():
        messages.error(request, "You must be an approved member of this room to submit quizzes")
        return redirect('room', pk=pk)
    
    if request.method == 'POST':
        # Here you could process the form data and save quiz results
        # For now, we're just redirecting back
        messages.success(request, "Quiz completed successfully!")
    else:
        messages.info(request, "Returning to room without submitting quiz")
    
    return redirect('room', pk=room.id)
