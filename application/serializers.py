from rest_framework import serializers
from .models import Menage

class MenageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menage
        fields = '__all__'
