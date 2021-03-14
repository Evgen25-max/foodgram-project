from django import template
from django.template.defaultfilters import floatformat

from users.models import BasketUser, Favorite, Subscription

register = template.Library()


@register.filter
def addclass(field, css):
    """Add class for form fields."""

    return field.as_widget(attrs={"class": css})


@register.filter
def recipe_basket_check(recipe, request):
    """Checks whether the recipe is in the shopping cart."""

    if request.user.is_authenticated:
        return BasketUser.objects.filter(recipe=recipe, user=request.user).exists()
    basket_recipes = request.session.get('basket_recipes')
    if basket_recipes:
        return str(recipe.pk) in basket_recipes
    return False


@register.filter
def subscriptions_check(author, user):
    """Checking whether the recipe is in the hands of selected authors?."""

    if user.is_authenticated:
        return Subscription.objects.filter(author=author, user=user).exists()
    return False


@register.filter
def favorite_check(recipe, user):
    """Checking whether the recipe is in favorite recipes?"""

    return Favorite.objects.filter(recipe=recipe, user=user).exists()


@register.filter
def formatted_float(value):
    """Replacing the comma with a dot.."""

    value = floatformat(value)
    return str(value).replace(',', '.')


@register.filter
def shop_count(user, request):
    """Number of recipes in the shopping cart."""

    if user.is_authenticated:
        return BasketUser.objects.filter(user=user).count()
    recipe_list = request.session.get('basket_recipes')
    if recipe_list is None:
        return 0
    return len(recipe_list)


@register.filter
def sub_up_0(minuend, subtrahend):
    """Returns the positive value of the difference between the numbers (otherwise 0)."""

    answer = minuend - subtrahend
    if answer < 0:
        return 0
    return answer
