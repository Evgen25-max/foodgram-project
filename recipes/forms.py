from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from .models import Recipe, RecipeTag
from .utils import get_ingredients, ingredients_exist

# class Active_reciep
class RecipeForm(ModelForm):
    """Form for recipes create."""

    recipe_tag = ModelMultipleChoiceField(
        queryset=RecipeTag.objects.all(),
        to_field_name='meal_time'
    )

    class Meta:
        model = Recipe
        fields = ['title', 'recipe_tag', 'description', 'cooking_time', 'image']

    def clean(self):
        cleaned_data = super().clean()
        ingredients = get_ingredients(self.data)
        if ingredients:
            valid_ingredient = ingredients_exist(ingredients)
        else:
            raise ValidationError(_('Необходимо указать хотя бы один ингридиент'))
        if valid_ingredient:
            cleaned_data.update({'ingredients': valid_ingredient})
        return cleaned_data
