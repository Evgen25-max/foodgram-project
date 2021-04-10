from collections import OrderedDict

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from recipes.models import BasketUser, Favorite, Ingredient
from users.models import Subscription

from .const import METHOD_PERMISSIONS
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
    filterset_class = IngredientFilterSet

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response([OrderedDict([('title', ''), ('dimension', '')])])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubscriptionViewSet(CreateDestroyViewSet):
    """ViewSet for the Subscription model."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        return get_obj_method_permissions(self, **METHOD_PERMISSIONS[self.basename])

    def destroy(self, request, *args, **kwargs):
        author = kwargs.get('pk')
        if not author:
            raise Http404
        instance = get_object_or_404(self.queryset, user=request.user, author=author)
        self.perform_destroy(instance)
        return Response({'success': True})

    def perform_create(self, serializer):
        """Save instance with/without data about user."""

        if 'user' not in serializer.validated_data:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class FavoriteViewSet(SubscriptionViewSet):
    """ViewSet for the Favorite model."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def destroy(self, request, *args, **kwargs):
        recipe_pk = kwargs.get('pk')
        if not recipe_pk:
            raise Http404

        instance = get_object_or_404(self.queryset, recipe=recipe_pk, user=request.user)
        self.check_object_permissions(self.request, instance)
        self.perform_destroy(instance)
        return Response({'success': True}, status=status.HTTP_200_OK)


class BasketViewSet(SubscriptionViewSet):
    """ViewSet for the BasketUser model."""

    queryset = BasketUser.objects.all()
    serializer_class = BasketUserSerializer

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
        return Response({'success': True}, status=status.HTTP_200_OK)
