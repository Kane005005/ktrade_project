from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat-list'),
    path('conversation/<int:conversation_id>/', views.chat_detail, name='chat-detail'),
    path('start/<int:user_id>/', views.start_conversation, name='start-chat'),
    path('api/messages/<int:conversation_id>/', views.get_messages, name='get-messages'),
    path('api/send-message/', views.send_message, name='send-message'),
    path('api/mark-read/<int:message_id>/', views.mark_as_read, name='mark-read'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-read'),
]