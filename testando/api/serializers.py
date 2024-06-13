from rest_framework import serializers
from .. import models

class ImagesSeriaizer(serializers.ModelSerializer):
    class Meta:
        model = models.Images
        fields = '__all__'
