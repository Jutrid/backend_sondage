from rest_framework import serializers
from .models import Menage, Distribution, Articles, Bouquets, Besoin

class MenageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menage
        fields = '__all__'

class DistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribution
        fields = '__all__'

class BesoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Besoin
        fields = '__all__'

class BouquetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bouquets
        fields = '__all__'
