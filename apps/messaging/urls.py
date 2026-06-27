from django.urls import path
from . import views



urlpatterns = [
    path('', views.my_conversations, name='my_conversations'),
    path('<int:conversation_id>/', views.my_conversations, name='chat_view'),
]