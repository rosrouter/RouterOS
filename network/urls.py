from rest_framework import routers
from django.urls import path, include

app_name = "network"
router = routers.DefaultRouter()

urlpatterns = [
    path(r'', include(router.urls)),
]
