from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Chat rooms
    path('rooms/', views.ChatRoomListView.as_view(), name='room-list'),
    path('rooms/create/', views.ChatRoomCreateView.as_view(), name='room-create'),
    path('rooms/<int:pk>/', views.ChatRoomDetailView.as_view(), name='room-detail'),
    path('rooms/<int:chat_room_id>/read/', views.mark_chat_room_read, name='room-mark-read'),
    path('rooms/<int:chat_room_id>/delete/', views.delete_chat_room, name='room-delete'),
    path('rooms/search/', views.ChatRoomSearchView.as_view(), name='room-search'),
    
    # Messages
    path('rooms/<int:chat_room_id>/messages/', views.MessageListView.as_view(), name='message-list'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message-create'),
    path('messages/read/', views.MessageReadView.as_view(), name='message-read'),
    
    # Notifications
    path('notifications/', views.ChatNotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='notification-read-all'),
    
    # Utilities
    path('unread-count/', views.unread_count, name='unread-count'),
] 