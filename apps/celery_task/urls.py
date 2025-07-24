from django.urls import path, include
from .views import TestView
urlpatterns = [
    path('api/test', TestView.as_view())
]
