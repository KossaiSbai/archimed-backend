from .models import Company, Shop, Draft, Label, CustomUser, Product
from rest_framework import serializers
class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ['url', 'id', 'name', 'created_at', 'updated_at']