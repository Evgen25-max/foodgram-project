from django import template
from django.template.defaultfilters import floatformat

from recipes.models import BasketUser

register = template.Library()


@register.filter
def addclass(field, css):
    """Add class for form fields."""

    return field.as_widget(attrs={"class": css})


@register.filter
def recipe_basket_check(recipe, request):
    """Checks whether the recipe is in the shopping cart."""

    basket_recipes = request.session.get('basket_recipes')
    if basket_recipes:
        return str(recipe.pk) in basket_recipes
    return False


@register.filter
def formatted_float(value):
    """Replacing the comma with a dot.."""

    value = floatformat(value)
    return str(value).replace(',', '.')


@register.filter
def shop_count(user, request):
    """Number of recipes in the shopping cart."""

    if user.is_authenticated:

        return BasketUser.objects.filter(user=user).count() or ''
    recipe_list = request.session.get('basket_recipes')
    if not recipe_list:
        return ''
    return len(recipe_list)


@register.filter
def correct_ending(number, word):
    """Remainder for word (parent case)."""

    remainder_dict = {
        (2, 3, 4): 'а',
        (0, 5, 6, 7, 8, 9): 'ов',
        (1,): '',
    }
    remainder = number % 100
    if remainder in range(11,20):
        return f'{number} {word}ов'
    remainder = remainder % 10
    for key in remainder_dict:
        if remainder in key:
            remainder = remainder_dict[key]
            break
    return f'{number} {word}{remainder}'
