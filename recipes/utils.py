import re
from collections import defaultdict
from io import BytesIO
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from .const import GIT_HUB, PROJECT_NAME
from .models import Ingredient, RecipeIngredient


def get_actual_tag(path):

    tags = ['breakfast', 'lunch', 'dinner']
    temp_actual_tags = {}
    for tag in tags:
        temp_tag = re.search(rf'{tag}=\d', path)
        if not temp_tag:
            temp_actual_tags[tag] = 1
    return temp_actual_tags


def get_ingredients(data):
    """Get all the ingredients from the recipe."""

    temp_ingredient_data = []
    ingredient_actual = []
    if data:
        for key in data:
            if 'nameIngredient_' in key:
                index_ingredient = key.split('_', maxsplit=1)[1]
                try:
                    temp_ingredient_data.append(data[f'nameIngredient_{index_ingredient}'])
                except KeyError:
                    raise ValidationError(_('Незаполнено название ингредиента'))
                try:
                    temp_ingredient_data.append(data[f'unitsIngredient_{index_ingredient}'])
                except KeyError:
                    raise ValidationError(_('Незаполнена мера измерения ингредиента'))
                try:
                    temp_ingredient_data.append(float(data[f'valueIngredient_{index_ingredient}']))
                except KeyError:
                    raise ValidationError(_('Незаполнено количество ингредиента'))
                except ValueError:
                    raise ValidationError(_('Количество ингредиента должно быть числом'))

                ingredient_actual.append(
                    {
                     'amount': temp_ingredient_data.pop(),
                     'ingredient': {'dimension': temp_ingredient_data.pop(),'title': temp_ingredient_data.pop()}}
                )

    return ingredient_actual


def ingredients_save(ingredients, recipe):
    """Saving the ingredients in the recipe."""
    RecipeIngredient.objects.filter(recipe=recipe).delete()
    recipe_ingerient = []
    for ingredient in ingredients:
        recipe_ingerient.append(
            RecipeIngredient(amount=ingredients[ingredient], recipe=recipe, ingredient=ingredient,)
        )

    RecipeIngredient.objects.bulk_create(recipe_ingerient)
    return recipe_ingerient


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def get_ingredient_dict(recipe_ingredients):
    """Returns a dictionary ingredients of the form {(ingredient, dimension): quantity, ...}."""

    ing_for_file = defaultdict(int)
    for recipe_ingredient in recipe_ingredients:
        ing_for_file[(recipe_ingredient.ingredient.title, recipe_ingredient.ingredient.dimension)] += recipe_ingredient.amount # noqa
    return ing_for_file


def pdf_get(ingredient_for_file):
    """Returns a pdf file with the ingredients."""

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Your shopping list.pdf"'
    buffer = BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    y = 750
    draw_header_pdf(page, 'FreeSans', 24)
    page.setFont('FreeSans', 16)
    count = 0

    for ingredient in ingredient_for_file:
        if count < 34:
            str = f'• {ingredient[0]}({ingredient[1]}) - {ingredient_for_file[ingredient]}'
            page.drawString(100, y, str)
            y -= 20
            count += 1
        else:
            draw_footer_pdf(page, 'FreeSansOblique', 20)
            page.showPage()
            page.setPageSize(size=A4)
            draw_header_pdf(page, 'FreeSans', 24)
            page.setFont('FreeSans', 16)
            y = 750
            count = 0
    draw_footer_pdf(page, 'FreeSansOblique', 20)

    page.showPage()
    page.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def draw_header_pdf(page, font, size):
    """Write the project name in the page header."""

    page.setFont(font, size)
    page.drawString(150, 800, PROJECT_NAME)


def draw_footer_pdf(page, font, size):
    """Write the author's github to the footer page."""

    page.setFont(font, size)
    page.drawString(150, 50, GIT_HUB)


def ingredients_exist(recipe_ingredients):
    """Returns valid ingredients in the form: {Ingredient instance: quantity}."""

    ingredients_clean = {}
    broken_ingredient = []
    for ingredient in recipe_ingredients:
        ingredient_instance = get_or_none(Ingredient, title=ingredient['ingredient']['title'], dimension=ingredient['ingredient']['dimension'])
        if not ingredient_instance:
            broken_ingredient.append(f"некорректный ингредиент: {ingredient['ingredient']['title']}")
        else:
            if ingredients_clean.get(ingredient_instance):
                broken_ingredient.append(f"повторяющийся ингредиент: {ingredient['ingredient']['title']}")
            else:
                ingredients_clean.update({ingredient_instance: ingredient['amount']})
    if broken_ingredient:
        ingr_for_error = ', '.join(broken_ingredient)
        raise ValidationError(
                _(f"Ошибка: {ingr_for_error}.\n При необходимости воспользуйтесь выпадающим списком ингредиентов")
            )

    return ingredients_clean


def ingredients_change(recipe_ing, form_ing):
    """Returns valid ingredients in the form: {Ingredient instance: quantity}."""

    if len(recipe_ing) == len(form_ing):
        for recipe_ingredient in recipe_ing:
            if not (
                    recipe_ingredient.ingredient in form_ing and
                    form_ing[recipe_ingredient.ingredient] == recipe_ingredient.amount
            ):
                return True
        return False
    return True

def paginator_initial(request, model_objs, paginator_count):
    """:"""

    paginator = Paginator(model_objs, paginator_count)
    page_number = request.GET.get('page')
    if page_number and int(page_number) > paginator.num_pages:
        page = paginator.get_page(paginator.num_pages)
    else:
        page = paginator.get_page(page_number)
    return page, paginator
