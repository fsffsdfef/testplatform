from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register("log", views.Log, basename='case')
urlpatterns = [
    path("api/", include(router.urls)),
    path('logs/', views.log_list_view, name='log_list'),
    path('logs/<int:log_id>/', views.log_detail_view, name='log_detail'),
    path('logs/statistics/', views.log_statistics_view, name='log_statistics'),
    path('logs/cleanup/', views.log_cleanup_view, name='log_cleanup'),
]