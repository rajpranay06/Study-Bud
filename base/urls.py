from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='base/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='base/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='base/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='base/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    path('', views.home, name='home'),
    path('room_page/<str:pk>/', views.room, name='room'),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>', views.deleteRoom, name='delete-room'),
    path('delete-message/<str:pk>', views.deleteMessage, name='delete-message'),

    path('update-user/', views.updateUser, name='update-user'),
    path('change-password/', views.changePassword, name='change-password'),
    path('change-password-page/', views.changePasswordPage, name='change-password-page'),
    
    path('topics/', views.topicsPage, name='topics'),
    path('activity/', views.activityPage, name='activity'),

    path('poll/<int:poll_id>/vote/<int:option_id>/', views.vote_poll, name='vote-poll'),
    path('message/<int:message_id>/react/', views.add_emoji_reaction, name='add-emoji-reaction'),
    path('create-poll/<int:pk>/', views.create_poll, name='create-poll'),
    
    # Join request URLs
    path('room/<str:pk>/request-join/', views.request_join_room, name='request-join-room'),
    path('room/<str:pk>/join-requests/', views.manage_join_requests, name='manage-join-requests'),
    path('join-request/<int:request_id>/<str:action>/', views.process_join_request, name='process-join-request'),
    
    # Quiz URLs
    path('generate-quiz/<str:pk>/', views.generate_quiz, name='generate-quiz'),
    path('submit-quiz/<str:pk>/', views.submit_quiz, name='submit-quiz'),
]
