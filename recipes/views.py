from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Subquery
from django.shortcuts import get_object_or_404, redirect, render

from recipes.models import Favorite, Recipe, RecipeIngredient
from users.models import Subscription

from .forms import RecipeForm
from .utils import (get_actual_tag, get_ingredients, get_or_none,
                    ingredients_change, paginator_initial, pdf_get)

User = get_user_model()


def page_not_found(request, exception):

    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def index(request):
    """ """

    actual_tags = get_actual_tag(request.get_full_path())

    recipes = Recipe.objects.recipe_with_tag(tag=actual_tags).annotate_subscribe_favorite(user=request.user)
    page, paginator = paginator_initial(request, recipes, settings.PAGINATOR_COUNT['default'])
    return render(
        request, 'recipes/indexAuth.html', {'page': page, 'paginator': paginator}
    )


def profile(request, username):
    """."""

    actual_tags = get_actual_tag(request.get_full_path())
    author = get_object_or_404(User.objects.filter(username=username))
    recipes = author.recipes.recipe_with_tag(tag=actual_tags).annotate_all(user=request.user)
    page, paginator = paginator_initial(request, recipes, settings.PAGINATOR_COUNT['default'])
    sub = request.user.is_authenticated and get_or_none(Subscription, user=request.user, author=author)
    return render(
        request,
        'recipes/authorRecipe.html',
        {'page': page, 'paginator': paginator, 'author': author, 'sub': sub}
    )


def subscriptions(request):
    """."""

    follow_user = Subscription.objects.filter(
        user=request.user).annotate(num_recipes=Count('author__recipes')).prefetch_related('author__recipes')

    paginator = Paginator(follow_user, settings.PAGINATOR_COUNT['subscribe'])
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'recipes/myFollow.html', {'page': page, 'paginator': paginator, 'follow_user': follow_user}
    )


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        form.instance.author = request.user
        recipe_ingredient = form.cleaned_data.get('ingredients')
        if recipe_ingredient:
            form.save(recipe_ingredient)
            return redirect('recipes:index')
    ingredients = get_ingredients(form.data)
    return render(request, 'recipes/formRecipe.html', {'form': form, 'ingredients': ingredients})


def recipe_view(request, username, recipe_id):

    recipe = get_object_or_404(
        Recipe.objects.filter(
            pk=recipe_id,
            author__username=username
        ).select_related('author').prefetch_related(
            'recipe_ingredient__ingredient', 'recipe_tag'
        ).annotate_all(user=request.user))
    return render(
        request,
        'recipes/singlePage.html',
        {'recipe': recipe}
    )


@login_required
def recipe_remove(request, username, recipe_id):
    """"""
    recipe = get_object_or_404(Recipe.objects.filter(pk=recipe_id, author__username=username))
    if recipe.author == request.user:
        recipe.delete()
    return redirect('recipes:index')


@login_required
def recipe_edit(request, username, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.filter(
            author__username=username, pk=recipe_id
        ).prefetch_related(
            'recipe_tag', Prefetch(
                'ingredients', queryset=RecipeIngredient.objects.filter(
                    recipe__pk=recipe_id
                ).select_related('ingredient')
            )
        )
    )

    if request.user == recipe.author:
        form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)
        if form.is_valid():
            if (ingredients_change(form.instance.ingredients.all(), form.cleaned_data.get('ingredients')) or
                    form.has_changed()):
                recipe = form.save()

                return redirect('recipes:index')

            return render(request, 'recipes/formRecipe.html', {'form': form, 'recipe': recipe})
        ingredients = get_ingredients(form.data) or recipe.ingredients.all()
        return render(request, 'recipes/formRecipe.html', {'form': form, 'recipe': recipe, 'ingredients': ingredients})
    return redirect('recipes:recipe', username=username, recipe_id=recipe_id)


@login_required
def favorite(request, username):
    """."""

    actual_tags = get_actual_tag(request.get_full_path())
    favorites_user = get_object_or_404(User.objects.filter(username=username))
    favorite_recipe = Favorite.objects.filter(user__username=username)
    recipes = Recipe.objects.filter(
        pk__in=Subquery(
            favorite_recipe.values('recipe')
        )).recipe_with_tag(actual_tags).annotate_subscribe_favorite(user=request.user)
    page, paginator = paginator_initial(request, recipes, settings.PAGINATOR_COUNT['default'])
    return render(request, 'recipes/indexAuth.html',
                  {'page': page, 'paginator': paginator, 'author': favorites_user})


def shoplist(request):
    """."""

    if request.user.is_authenticated:
        recipes = Recipe.objects.filter(basket_recipe__user=request.user)
    else:
        basket_recipes = request.session.get('basket_recipes')
        if basket_recipes:
            try:
                recipes = Recipe.objects.filter(pk__in=[int(recipe_pk) for recipe_pk in basket_recipes])
            except ValueError:
                request.session.pop('basket_recipes')
                recipes = None
        else:
            recipes = None

    return render(request, 'recipes/shopList.html',
                  {'recipes': recipes, })


def shoplist_file(request):
    """."""
    if request.user.is_authenticated:
        recipes = RecipeIngredient.objects.filter(
            recipe__basket_recipe__user=request.user
        ).select_related('ingredient')
    else:
        recipes = request.session.get('basket_recipes')
        if recipes:
            try:
                recipes = RecipeIngredient.objects.filter(
                    recipe__pk__in=recipes
                ).select_related('ingredient')

            except ValueError:
                request.session.pop('basket_recipes')
                recipes = {}
        else:
            recipes = {}

    return pdf_get(recipes)
