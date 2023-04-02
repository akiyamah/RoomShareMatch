from django.urls import path
from . import views

app_name = 'messages_app'

urlpatterns = [
    path('list/', views.message_list, name='message_list'),
    path('view_chat/<str:receiver_id>/', views.view_chat, name='view_chat'),
    path('send_message/<int:receiver_id>/<uuid:chat_id>/', views.send_message_view, name='send_message_view'),
]
