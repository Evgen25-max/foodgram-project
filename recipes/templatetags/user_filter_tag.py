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
def correct_ending(number, ending):
    """Remainder for word (parent case). Give count and 3 options ending. """

    ending_all = ending.split(',')
    try:
        remainder_dict = {
            (0, 5, 6, 7, 8, 9): ending_all[0],
            (1,): ending_all[1],
            (2, 3, 4): ending_all[2],
        }
    except IndexError:
        return 'Improper use of the filter'
    remainder = number % 100
    if remainder in range(11, 19):
        return f'{ending_all[0]}'
    remainder = remainder % 10
    return [remainder_dict[key] for key in remainder_dict if remainder in key][0]
