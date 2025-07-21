from django.urls import path, include
from rest_framework import routers
from .views import suit_view


router = routers.DefaultRouter()


urlpatterns = [
    path("api/", include(router.urls)),
    path("api/suit/getPageList", suit_view),
    path("api/suit/add", suit_view),
    path("api/suit/del", suit_view),
    path("api/suit/update", suit_view)
]
