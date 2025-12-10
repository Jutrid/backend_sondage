from rest_framework import serializers
from .models import Menage, Distribution, Articles, Bouquets, Besoin, ItemDistribution
from django.contrib.auth.models import User

class ItemDistribueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemDistribution
        fields = ["article", "quantite"]

class MenageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menage
        fields = '__all__'

class DistributionSerializer(serializers.ModelSerializer):
    items = ItemDistribueSerializer(many=True)
    fournisseurid = serializers.IntegerField(write_only=True)
    menage_uuid = serializers.CharField(write_only=True)

    class Meta:
        model = Distribution
        fields = [
            "date_distribution",
            "fournisseurid",
            "menage_uuid",
            "items",
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        fournisseur_id = validated_data.pop("fournisseurid")
        menage_uuid = validated_data.pop("menage_uuid")

        # Get or create Menage
        menage, _ = Menage.objects.get_or_create(uuid=menage_uuid)

        # Get fournisseur
        fournisseur = User.objects.get(id=fournisseur_id)

        # Create Distribution
        distribution = Distribution.objects.create(
            date_distribution=validated_data["date_distribution"],
            fournisseurid=fournisseur,
            menage=menage
        )

        # Create items
        for item in items_data:
            ItemDistribution.objects.create(
                distribution=distribution,
                article=item["article"],
                quantite=item["quantite"],
            )

        return distribution

class BesoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Besoin
        fields = '__all__'

class BouquetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bouquets
        fields = '__all__'

class ArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = '__all__'
