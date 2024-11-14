from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chatbot, name='chatbot'),
    path('voice_to_text/', views.voice_to_text, name='voice_to_text'),
    
]