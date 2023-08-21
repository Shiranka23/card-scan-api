from rest_framework import serializers
from .models import CardData

class ImageUploadSerializer(serializers.Serializer):
    class Meta:
        model=CardData
        fields=('image')