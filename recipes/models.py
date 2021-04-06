from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from users.models import Subscription

from .const import TAG_COLOR, TAG_RECIPE, TAG_RUS

User = get_user_model()


class RecipeTag(models.Model):
    """Tag model (meal time)."""

    meal_time = models.CharField(
        max_length=20, choices=TAG_RECIPE.choices, unique=True, verbose_name=_('meal for time')
    )
    color = models.CharField(max_length=20, null=True, editable=False)
    tag_russian = models.CharField(max_length=20, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.color = TAG_COLOR[self.meal_time]
        self.tag_russian = TAG_RUS[self.meal_time]
        super().save(self, *args, **kwargs)

    def __str__(self):
        return self.meal_time

    class Meta:
        verbose_name = _('Тег рецепта')
        verbose_name_plural = _('Теги рецепта')


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
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
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
        verbose_name = _("Ингредиент для рецепта")
        verbose_name_plural = _("Игридиенты для рецепта")
        unique_together = ['recipe', 'ingredient']


class RecipeQuerySet(models.QuerySet):
    def basket(self, **kwargs):
        return self.annotate(basket=Exists(BasketUser.objects.filter(recipe=OuterRef('pk'), **kwargs)))

    def favorite(self, **kwargs):
        return self.annotate(favorite=Exists(Favorite.objects.filter(recipe=OuterRef('pk'), **kwargs)))

    def subscribe(self, **kwargs):
        return self.annotate(subscribe=Exists(Subscription.objects.filter(author=OuterRef('author'), **kwargs)))

    def recipe_with_tag(self, tag):
        return self.filter(
            recipe_tag__meal_time__in=tag
        ).select_related('author').prefetch_related('recipe_tag').distinct()

    def annotate_basket_favorite(self, **kwargs):
        return self.annotate(
            basket=Exists(BasketUser.objects.filter(recipe=OuterRef('pk'), **kwargs)),
            favorite=Exists(Favorite.objects.filter(recipe=OuterRef('pk'), **kwargs))
        )

    def annotate_all(self, **kwargs):
        return self.annotate(
            basket=Exists(BasketUser.objects.filter(recipe=OuterRef('pk'), **kwargs)),
            favorite=Exists(Favorite.objects.filter(recipe=OuterRef('pk'), **kwargs)),
            subscribe=Exists(Subscription.objects.filter(author=OuterRef('author'), **kwargs))
        )


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
        _('cooking time'), help_text=_('enter the cooking time in minutes'),
        validators=(
            MinValueValidator(1, 'Время приготовление должно быть больше 0 :-)'),
            MaxValueValidator(32767, 'Время приготовление должно быть меньше 32767. Это ну очень долго :-)'),
        ),
    )
    pub_date = models.DateTimeField(_('publication date'), auto_now_add=True)

    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ['-pub_date']
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')

    def get_absolute_url(self):
        return reverse('recipes:recipe', args=[self.author, self.pk])
    # def get_absolute_url(self):
    #     return reverse('recipes:recipe', kwargs={'pk': self.pk})
    def __str__(self):
        return self.title


class Favorite(models.Model):
    """Model of selected recipes."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_fav')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_fav')

    class Meta:
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f'{self.recipe} is favorites for {self.user}'


class BasketUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='basket_user')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='basket_recipe')

    class Meta:
        unique_together = ['user', 'recipe']
