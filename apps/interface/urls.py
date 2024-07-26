from django.urls import path, include
from rest_framework import routers
from apps.interface.views import *
router = routers.DefaultRouter()
router.register('apply', ApplyView, basename='apply')
router.register('port', PortView, basename='port')

urlpatterns = [
    path('api/', include(router.urls))
]