from rest_framework import viewsets, permissions
from .serializers import ImagesSeriaizer
from ..models import Images

class ImagesViewset(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImagesSeriaizer
    permission_classes = [permissions.AllowAny]
