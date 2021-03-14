from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from recipes.models import Ingredient
from users.models import BasketUser, Favorite, Subscription

from .const import BASKET_USER_METHOD_PERMISSIONS, FAVORITE_METHOD_PERMISSIONS
from .filters import IngredientFilterSet
from .serializers import (BasketUserSerializer, FavoriteSerializer,
                          IngredientSerializer, SubscriptionSerializer)


class ListViewSet(
    ListModelMixin,
    GenericViewSet,
):
    """A viewset that provides `create()`,  delete() and `list()` actions."""

    pass


class CreateDestroyViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """A viewset that provides `create()`,  delete() and `list()` actions."""

    pass


def get_obj_method_permissions(self, **kwargs):
    """Returns permissions for the request method."""

    method = self.request.method
    try:
        permission_classes = kwargs[method]
    except KeyError:
        raise MethodNotAllowed(method)
    return (permission() for permission in permission_classes)


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet for the Ingredient model."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilterSet


class SubscriptionViewSet(CreateDestroyViewSet):
    """ViewSet for the Subscription model."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        return get_obj_method_permissions(self, **FAVORITE_METHOD_PERMISSIONS)

    def destroy(self, request, *args, **kwargs):
        author = kwargs.get('pk')
        if not author:
            raise Http404
        instance = get_object_or_404(self.queryset, user=request.user, author=author)
        self.perform_destroy(instance)
        return Response({"success": True})


class FavoriteViewSet(CreateDestroyViewSet):
    """ViewSet for the Favorite model."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_permissions(self):
        return get_obj_method_permissions(self, **FAVORITE_METHOD_PERMISSIONS)

    def destroy(self, request, *args, **kwargs):
        recipe_pk = kwargs.get('pk')
        if not recipe_pk:
            raise Http404

        instance = get_object_or_404(self.queryset, recipe=recipe_pk, user=request.user)
        self.check_object_permissions(self.request, instance)
        self.perform_destroy(instance)
        return Response({"success": True})


class BasketViewSet(CreateDestroyViewSet):
    """ViewSet for the BasketUser model."""

    queryset = BasketUser.objects.all()
    serializer_class = BasketUserSerializer

    def get_permissions(self):
        return get_obj_method_permissions(self, **BASKET_USER_METHOD_PERMISSIONS)

    def create(self, request, *args, **kwargs):
        """Adding a recipe to the shopping cart for an authorized and anonymous user."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.is_authenticated:
            self.perform_create(serializer)
        else:
            if request.session.get('basket_recipes'):
                request.session['basket_recipes'].append(serializer.initial_data['id'])
                request.session.modified = True
            else:
                request.session['basket_recipes'] = [serializer.initial_data['id']]
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        """Deleting a recipe from the trash for an authorized and anonymous user."""
        recipe_pk = kwargs.get('pk')
        if not recipe_pk:
            raise Http404
        if request.user.is_authenticated:
            instance = get_object_or_404(self.queryset, recipe=recipe_pk, user=request.user)
            self.check_object_permissions(self.request, instance)
            self.perform_destroy(instance)
        else:
            if request.session.get('basket_recipes'):
                try:
                    request.session['basket_recipes'].remove(recipe_pk)
                    request.session.modified = True
                except (KeyError, ValueError):
                    return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"success": True})
