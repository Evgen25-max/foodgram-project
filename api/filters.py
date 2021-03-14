from django_filters import rest_framework

from recipes.models import Ingredient


class IngredientFilterSet(rest_framework.FilterSet):
    """Filter for ingredient models."""

    query = rest_framework.CharFilter(
        field_name='title',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = (
            'query',
        )
