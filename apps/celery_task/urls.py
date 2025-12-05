from django.urls import path, include
from rest_framework import routers
from .views import *
router = routers.DefaultRouter()
router.register("task", PeriodcTaskView, basename="task")
router.register("tasks", PeriodcTasksView, basename="tasks")
router.register("interval", IntervalScheduleView, basename="interval")
router.register("clocked", ClockedScheduleView, basename="clocked")
router.register("crontab", CrontabScheduleView, basename="crontab")
router.register("solar", SolarScheduleView, basename="solar")
urlpatterns = [
    path("api/", include(router.urls)),
    path('api/test', TestView.as_view())
]
