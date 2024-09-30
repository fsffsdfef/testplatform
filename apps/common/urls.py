from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.common.views.depart_app_menu_view import *
from apps.common.views.user_role_permissions_group_view import *
from apps.common.views.token_view import MyObtainTokenPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

router = routers.DefaultRouter()
router.register('depart', DepartView, basename='depart')
router.register('apply', ApplyView, basename='apply')
router.register('permission', PermissionView, basename='permission')
router.register('group', GroupView, basename='group')
router.register('role', RoleView, basename='role')
router.register('user', UserView, basename='user')
router.register('menu', MenuViewA, basename='menu')
# router.register('express', ExpressView, basename='express')
# router.register('expressitem', ExpressItemView, basename='expressitem')
urlpatterns = [
    path('api/', include(router.urls)),
    # 获取Token接口
    path('api/token/', MyObtainTokenPairView.as_view(), name='login'),
    # 获取Token有效期的接口
    path('api/refresh/', TokenRefreshView.as_view(), name="refresh"),
    # 获取Token的有效性
    path('api/token/verify/', TokenVerifyView.as_view(), name="token_verify"),
    path('api/menu1/', MenuView.as_view(), name="menu1")
]