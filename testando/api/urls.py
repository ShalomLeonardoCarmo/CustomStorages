from rest_framework import routers
from django.urls import path, include
from .views import ImagesViewset

router = routers.DefaultRouter()
router.register('images', ImagesViewset)

urlpatterns = [
    path('', include(router.urls))
]

