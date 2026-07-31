# config/routing.py
from django.urls import path
from apps.celery_task.consumers import UserChannelConsumer, TaskChannelConsumer

websocket_urlpatterns = [
    path("ws/user/<str:user_id>/", UserChannelConsumer.as_asgi()),
    path("ws/task/<str:task_id>/", TaskChannelConsumer.as_asgi()),
]