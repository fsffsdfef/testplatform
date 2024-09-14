from django.urls import path, include
from rest_framework import routers
from apps.automation.views.interface.httpview import InterfaceHttpView
from apps.automation.views.interface.portview import PortView


router = routers.DefaultRouter()
router.register('httpcase', viewset=InterfaceHttpView, basename='httpcase')
router.register('port', viewset=PortView, basename='port')


urlpatterns = [
    path('api/', include(router.urls))
]
