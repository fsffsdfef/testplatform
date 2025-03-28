from django.urls import path, include
from rest_framework import routers
from .views.depart_apply_port import *
from .views.depart import depart_view
from .views.user import *

ROUTERS = {
    "depart/del": depart_view
}
router = routers.DefaultRouter()
router.register("user", UserView, basename="user")
#
# for k, v in ROUTERS.items():
#     router.register(k, viewset=v, basename=k)
urlpatterns = [
    path("api/", include(router.urls)),
    path("api/search", depart_view, name="search"),
    path("api/test", depart_view, name="test"),
    path("api/depart/getPageList", depart_view),
    path("api/depart/add", depart_view),
    path("api/depart/del", depart_view),
    path('api/login', TokenView.as_view(), name='login'),
]
