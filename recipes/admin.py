from django.contrib import admin

from users.models import Favorite

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag


class RecipeAdmin(admin.ModelAdmin):
    """Configuring the Recipe model for the admin panel."""

    list_display = (
        'pk',
        'title',
        'author',
        'count_favorite'
    )

    def count_favorite(self, obj):
        """Number of additions to favorites."""

        return Favorite.objects.filter(recipe=obj).count()

    search_fields = ('title', 'author__username', 'recipe_tag__meal_time',)
    empty_value_display = '-empty-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Configuring the RecipeIngredient model for the admin panel."""

    list_display = (
        'pk',
        'amount',
        )


class RecipeTagAdmin(admin.ModelAdmin):
    """Configuring the RecipeTag model for the admin panel."""

    list_display = (
        'pk',
        'meal_time',
        )


class IngredientAdmin(admin.ModelAdmin):
    """Configuring the Ingredient model for the admin panel."""

    list_display = (
           'title',
           'dimension',
        )
    search_fields = ('title',)
    empty_value_display = '-empty-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
