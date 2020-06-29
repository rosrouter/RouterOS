from rest_framework import routers
from django.urls import path, include
from network import views
app_name = "network"
router = routers.DefaultRouter()

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'image/', views.image_test),
    path(r'api/test/', views.apiechart),
]
