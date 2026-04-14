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
    path("api/", include(router.urls)),
    path('api/test', TestView.as_view()),
    path("api/task/getPageList", task_view),
    path("api/task/add", task_view),
    path("api/task/update", task_view),
    path("api/task/del", task_view),
    path("api/interval/getPageList", interval_view),
    path("api/getTask/getPageList", get_tasks)
]
#     path('api/test', TestView.as_view()),

#     path("api/task/add", periodc_task),
#     path("api/task/del", periodc_task),
#     path("api/task/update", periodc_task),
#     path("api/interval/getPageList", interval_schedule),
#     path("api/interval/add", interval_schedule),
#     path("api/interval/del", interval_schedule),
#     path("api/interval/update", interval_schedule),
#     path("api/clocked/getPageList", clocked_schedule),
#     path("api/clocked/add", clocked_schedule),
#     path("api/clocked/del", clocked_schedule),
#     path("api/clocked/update", clocked_schedule),
#     path("api/crontab/getPageList", crontab_schedule),
#     path("api/crontab/add", crontab_schedule),
#     path("api/crontab/del", crontab_schedule),
#     path("api/crontab/update", crontab_schedule),
#     path("api/solar/getPageList", solar_schedule),
#     path("api/solar/add", solar_schedule),
#     path("api/solar/del", solar_schedule),
#     path("api/solar/update", solar_schedule)
# ]
