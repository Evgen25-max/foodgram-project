from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import BasketUser, Favorite, Ingredient, Recipe
from users.models import Subscription

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient models."""

    class Meta:
        exclude = ('id',)
        model = Ingredient


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscription models."""

    id = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='id',
        source='author',
        write_only=True,
    )

    class Meta:
        fields = ('id',)
        model = Subscription
        extra_kwargs = {'user': {'read_only': True}}


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorite models."""

    id = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='pk',
        source='recipe',
        write_only=True,
    )

    class Meta:
        fields = ('id',)
        model = Favorite
        extra_kwargs = {'user': {'read_only': True}}


class BasketUserSerializer(serializers.ModelSerializer):
    """Serializer for Follow models."""

    id = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='pk',
        source='recipe',
        write_only=True,
    )

    class Meta:
        fields = ('id',)
        model = BasketUser
        extra_kwargs = {'user': {'read_only': True}}
