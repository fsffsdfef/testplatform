from django.urls import path, include
from rest_framework import routers
from .views import *
router = routers.DefaultRouter()
router.register("tasks", PeriodcTasksView, basename="tasks")
router.register("interval", IntervalScheduleView, basename="interval")
router.register("clocked", ClockedScheduleView, basename="clocked")
router.register("crontab", CrontabScheduleView, basename="crontab")
router.register("solar", SolarScheduleView, basename="solar")
router.register("task", PeriodcTaskView, basename="task")
urlpatterns = [
    path("api/", include(router.urls)),
    path('api/test', TestView.as_view()),
    # path("api/task/getPageList", task_view),
    # path("api/task/add", task_view),
    # path("api/task/del", task_view),
    # path("api/task/update", task_view)
]
