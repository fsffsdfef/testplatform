from django.urls import path, include
from rest_framework import routers
from .views.depart_apply_port import *
from .views.depart import depart_view
from .views.apply import apply_view
from .views.port import port_view
from .views.menu import *
from .views.user import *

ROUTERS = {
    "depart/del": depart_view
}
router = routers.DefaultRouter()
router.register("apply", ApplyView, basename="apply")
router.register("port", PortView, basename="port")
router.register("menu1", MenuInitializeView, basename='menu1')
router.register("card", MenuCascaderView, basename='card')
#
# for k, v in ROUTERS.items()
#     router.register(k, viewset=v, basename=k)
urlpatterns = [
    path("api/", include(router.urls)),
    path("api/search", depart_view, name="search"),
    path("api/depart/getPageList", depart_view),
    path("api/depart/add", depart_view),
    path("api/depart/del", depart_view),
    path("api/depart/update", depart_view),
    path("api/depart/batch", depart_view),
    path("api/apply/getPageList", apply_view),
    path("api/apply/add", apply_view),
    path("api/apply/del", apply_view),
    path("api/apply/update", apply_view),
    path("api/port/getPageList", port_view),
    path("api/port/add", port_view),
    path("api/port/del", port_view),
    path("api/port/update", port_view),
    path("api/user/getPageList", user_view),
    path("api/user/add", user_view),
    path("api/user/del", user_view),
    path("api/user/update", user_view),
    path("api/menu/getPageList", menu_view),
    path("api/menu/add", menu_view),
    path("api/menu/del", menu_view),
    path("api/menu/update", menu_view),
    path("api/per/getPageList", per_view),
    path("api/per/add", per_view),
    path("api/per/del", per_view),
    path("api/per/update", per_view),
    path("api/roles/getPageList", role_view),
    path("api/roles/add", role_view),
    path("api/roles/del", role_view),
    path("api/roles/update", role_view),
    path("api/groups/getPageList", group_view),
    path("api/groups/add", group_view),
    path("api/groups/del", group_view),
    path("api/groups/update", group_view),
    path('api/login', TokenView.as_view(), name='login')
]
