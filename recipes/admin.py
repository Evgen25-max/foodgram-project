from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """Configuring the Recipe model for the admin panel."""

    list_display = (
        'pk',
        'title',
        'cooking_time',
        'image',
        'author',
        'count_favorite'
    )

    inlines = (RecipeIngredientInline,)

    def count_favorite(self, obj):
        """Number of additions to favorites."""

        return obj.recipe_fav.count()

    count_favorite.short_description = 'Добавили в избранное'

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
