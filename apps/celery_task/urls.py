from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.celery_task.views import *
route_path = {
    'periodic': PeriodicTaskView,
    'periodics': PeriodicTasksView,
    'interval': IntervalScheduleView,
    'crontab': CrontabScheduleView,
    'clocked': ClockedScheduleView
}
router = routers.DefaultRouter()
for key, value in route_path.items():
    router.register(key, value, basename=key)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/task/', Demo.as_view()),
    path('api/demo/', Demo1.as_view()),
]
