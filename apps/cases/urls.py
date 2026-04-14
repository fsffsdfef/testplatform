from django.urls import path, include
from rest_framework import routers
from .views.interface_case_view import *
from .views.interface import httpcase_view


router = routers.DefaultRouter()
router.register("case", HttpCaseView, basename='case')
router.register("exp", ExpressItemView, basename="exp")
router.register("exs", ExpressView, basename="exs")
# router.register("two", TwoModelView, basename="two")
# router.register("three", ThreeModelView, basename="three")

urlpatterns = [
    path("api/", include(router.urls)),
    # path('api/bulk-create/', OneModelView.as_view({'post': 'bulk_create'})),
    path("api/httpcase/getPageList", httpcase_view),
    path("api/httpcase/add", httpcase_view),
    path("api/httpcase/del", httpcase_view),
    path("api/httpcase/update", httpcase_view),
    path("api/httpcase/batch", httpcase_view),
    path("api/operator/", operView)
]
