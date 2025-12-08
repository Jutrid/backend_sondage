from rest_framework import serializers
from .models import Menage, Distribution

class MenageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menage
        fields = '__all__'

class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = '__all__'
