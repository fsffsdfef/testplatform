from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.management.views import *

router = routers.DefaultRouter()
router.register('depart', DepartView, basename='depart')
urlpatterns = [
    path('api/', include(router.urls))
]