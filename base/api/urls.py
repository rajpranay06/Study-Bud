from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # Documentation routes
    path('', views.getRoutes),
    
    # Room routes
    path('rooms/', views.getRooms),
    path('rooms/<str:pk>/', views.getRoom),
    path('rooms/create/', views.createRoom, name='create-room-api'),
    path('rooms/<str:pk>/update/', views.updateRoom, name='update-room-api'),
    path('rooms/<str:pk>/delete/', views.deleteRoom, name='delete-room-api'),
    
    # Room-related routes
    path('rooms/<str:pk>/messages/', views.getRoomMessages),
    path('rooms/<str:pk>/polls/', views.getRoomPolls),
    path('rooms/<str:pk>/join-request/', views.createJoinRequest),
    path('rooms/<str:pk>/join-requests/', views.getRoomJoinRequests),
    
    # User routes
    path('users/', views.getUsers),
    path('users/<str:pk>/', views.getUser),
    
    # Topic routes
    path('topics/', views.getTopics),
    
    # Poll and message interaction routes
    path('polls/<str:poll_id>/vote/<str:option_id>/', views.votePoll),
    path('messages/<str:message_id>/react/', views.addEmojiReaction),
    
    # Join request routes
    path('join-requests/<str:pk>/', views.processJoinRequest),
    
    # GROQ API routes
    path('groq-chat/', views.groq_chat),
    path('generate-quiz/', views.generate_quiz_api),
    path('rooms/<str:pk>/generate-quiz/', views.generate_quiz_api),
]
