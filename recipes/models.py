from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .const import TAG_RECIPE

User = get_user_model()


class RecipeTag(models.Model):
    """Tag model (meal time)."""

    meal_time = models.CharField(
        max_length=20, choices=TAG_RECIPE.choices, unique=True, verbose_name=_('meal for time')
    )

    def __str__(self):
        return self.meal_time


class Ingredient(models.Model):
    """Model for ingredients."""

    title = models.CharField(
        _('the title of the ingredient'), max_length=200, help_text=_('Enter the title of the ingredient.'),
    )
    dimension = models.CharField(
        _('the unit of measurement of the ingredient'), max_length=10, help_text=_('dimension for ingredient')
    )

    class Meta:
        ordering = ['title']
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        unique_together = ['title', 'dimension']

    def __str__(self):
        return f'{self.title[:50]} with dimension: {self.dimension}'


class RecipeIngredient(models.Model):
    """An intermediate model between ingredients and recipes."""

    amount = models.FloatField(
        _('quantity of ingredient'),
        validators=(MinValueValidator(0, _('значение должно быть больше 0')),),
        help_text=_('input amount for ingredient')
    )
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='recipe_ingredient')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=True,)

    class Meta:
        verbose_name = _("Ingredient for recipe")
        verbose_name_plural = _("Ingredients for recipe")


class Recipe(models.Model):
    """Recipe model."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('author of recipe'), related_name='recipes'
    )
    title = models.CharField(
        _('the title of the recipe'), max_length=100, help_text=_('Enter the title of the recipe')
    )
    image = models.ImageField(
        _('image for recipe'), upload_to='recipes/', blank=True, null=True,
        default='recipes/defaultImage.png', help_text=_('Upload a recipe image')
    )
    description = models.TextField(
        _('Description of recipe'), blank=True, null=True, help_text=_('write a description of the recipe')
    )
    ingredients = models.ManyToManyField(
        Ingredient, through=RecipeIngredient, verbose_name=_('ingredient for recipe'),
        help_text=_('choose ingredients for your recipe')
    )
    recipe_tag = models.ManyToManyField(RecipeTag)

    cooking_time = models.PositiveSmallIntegerField(
        _('cooking time'), help_text=_('enter the cooking time in minutes')
    )
    pub_date = models.DateTimeField(_('publication date'), auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')

    def __str__(self):
        return self.title
