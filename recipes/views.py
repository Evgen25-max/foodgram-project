from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Subquery
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from recipes.models import Favorite, Recipe, RecipeIngredient
from users.models import Subscription

from .forms import RecipeForm
from .utils import (get_ingredients, get_or_none, ingredients_change,
                    paginator_initial, pdf_get)

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


class Index(ListView):
    """Index page view class."""

    template_name = 'recipes/indexAuth.html'
    paginate_by = settings.PAGINATOR_COUNT['default']

    def get_queryset(self):
        return Recipe.objects.recipe_with_tag(
            self.request.META.get('actual_tags')
        ).annotate_basket_favorite(user=self.request.user.pk)

    def paginate_queryset(self, queryset, page_size):
        return(paginator_initial(self.request, queryset, self.paginate_by))


class SubscriptionRecipe(LoginRequiredMixin, Index):
    """Page with subscribes users."""

    template_name = 'recipes/myFollow.html'
    paginate_by = settings.PAGINATOR_COUNT['subscribe']

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).annotate(
            num_recipes=Count('author__recipes')).prefetch_related('author__recipes'
                                                                   )


class FavoriteRecipe(LoginRequiredMixin, Index):
    """Page with favorite recipes users."""

    def get_queryset(self):
        self.author = get_object_or_404(User.objects.filter(username=self.kwargs['username']))
        favorite_recipe = Favorite.objects.filter(user__username=self.kwargs['username'])
        return Recipe.objects.filter(
            pk__in=Subquery(
                favorite_recipe.values('recipe')
            )).recipe_with_tag(self.request.META.get('actual_tags')).annotate_basket_favorite(
            user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context


class ProfileUser(Index):
    """All user recipes."""

    template_name = 'recipes/authorRecipe.html'

    def get_queryset(self):

        self.author = get_object_or_404(User.objects.filter(username=self.kwargs['username']))
        self.sub = self.request.user.is_authenticated and get_or_none(
            Subscription, user=self.request.user, author=self.author
        )
        return self.author.recipes.recipe_with_tag(
            self.request.META.get('actual_tags')
        ).annotate_all(
            user=self.request.user.pk
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['author'] = self.author
        context['sub'] = self.sub
        return context


class RecipeView(DetailView):
    """Single recipe page."""

    template_name = 'recipes/singlePage.html'
    context_object_name = 'recipe'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            Recipe.objects.filter(
                pk=self.kwargs['recipe_id'],
                author__username=self.kwargs['username']
            ).select_related('author').prefetch_related(
                'recipe_ingredient__ingredient', 'recipe_tag'
            ).annotate_all(user=self.request.user.pk))


class ShopList(ListView):
    """Users recipes in basket."""

    template_name = 'recipes/shopList.html'

    context_object_name = 'recipes'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.objects.filter(basket_recipe__user=self.request.user)
        else:
            basket_recipes = self.request.session.get('basket_recipes')
            recipes = None
            if basket_recipes:
                try:
                    return Recipe.objects.filter(pk__in=[int(recipe_pk) for recipe_pk in basket_recipes])
                except ValueError:
                    self.request.session.pop('basket_recipes')
                    return recipes


class NewRecipe(LoginRequiredMixin, CreateView):
    """Recipe add form."""

    template_name = 'recipes/formRecipe.html'
    form_class = RecipeForm

    def form_valid(self, form):

        form.instance.author = self.request.user
        recipe_ingredient = form.cleaned_data.get('ingredients')
        if recipe_ingredient:
            self.object = form.save(recipe_ingredient)
            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['ingredients'] = get_ingredients(context['form'])
        return context


class RecipeUpdate(UpdateView):
    """Recipe update form."""

    template_name = 'recipes/formRecipe.html'
    form_class = RecipeForm

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            Recipe.objects.filter(
                author__username=self.kwargs['username'], pk=self.kwargs['recipe_id']
            ).prefetch_related(
                'recipe_tag', Prefetch(
                    'ingredients', queryset=RecipeIngredient.objects.filter(
                        recipe__pk=self.kwargs['recipe_id']
                    ).select_related('ingredient')
                )
            )
        )

    def form_valid(self, form):
        if (ingredients_change(form.instance.ingredients.all(), form.cleaned_data.get('ingredients')) or
                form.has_changed()):
            self.object = form.save(form.cleaned_data['ingredients'])
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(
                self.request,
                'recipes/formRecipe.html',
                {'form': form, 'recipe': self.object, 'ingredients': form.instance.ingredients.all()}
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['ingredients'] = get_ingredients(context['form']) or self.object.ingredients.all()
        return context


class RecipeDelete(DeleteView):
    """Delete recipe."""

    model = Recipe
    success_url = reverse_lazy('recipes:index')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


def shoplist_file(request):
    """Uploads an ingredient purchase file to the user."""

    if request.user.is_authenticated:
        recipes_ingredients = RecipeIngredient.objects.filter(
            recipe__basket_recipe__user=request.user
        ).select_related('ingredient')
    else:
        recipes_pk_list = request.session.get('basket_recipes')
        if recipes_pk_list:
            try:
                recipes_ingredients = RecipeIngredient.objects.filter(
                    recipe__pk__in=recipes_pk_list
                ).select_related('ingredient')

            except ValueError:
                request.session.pop('basket_recipes')
                recipes_ingredients = {}
        else:
            recipes_ingredients = {}

    return pdf_get(recipes_ingredients)
