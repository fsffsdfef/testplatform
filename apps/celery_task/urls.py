from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register("tasks", PeriodicTasksView, basename="tasks")
router.register("interval", IntervalScheduleView, basename="interval")
router.register("clocked", ClockedScheduleView, basename="clocked")
router.register("crontab", CrontabScheduleView, basename="crontab")
router.register("solar", SolarScheduleView, basename="solar")
router.register("task", PeriodicTaskView, basename="task")

urlpatterns = [
    path('api/test', TestView.as_view()),
    path('api/test/async', TestAsyncView.as_view()),
    path("api/task/getPageList", task_view),
    path("api/task/add", task_view),
    path("api/task/update", task_view),
    path("api/task/del", task_view),
    path("api/interval/getPageList", interval_view),
    path("api/getTask/getPageList", get_tasks),
    path("api/task/runHistory", run_history_view),
    path("api/", include(router.urls)),
]