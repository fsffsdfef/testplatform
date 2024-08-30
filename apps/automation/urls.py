from django.urls import path, include
from rest_framework import routers
from apps.automation.views.interface.httpview import InterfaceHttpView


router = routers.DefaultRouter()
router.register('httpcase', viewset=InterfaceHttpView, basename='httpcase')


urlpatterns = [
    path('api/', include(router.urls))
]
