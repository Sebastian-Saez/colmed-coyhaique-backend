from rest_framework import serializers
from .models import Noticia
from django.contrib.auth.models import User
from base_colmed.serializers import UserSerializer

class NoticiaSerializer(serializers.ModelSerializer):
    autor = UserSerializer(read_only=True)

    class Meta:
        model = Noticia
        fields = '__all__'
