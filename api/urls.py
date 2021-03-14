from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BasketViewSet, FavoriteViewSet, IngredientViewSet,
                    SubscriptionViewSet)

router_v1 = DefaultRouter()

router_v1.register('ingredients', IngredientViewSet, basename='Ingredient')
router_v1.register('subscriptions', SubscriptionViewSet, basename='subscriptions')
router_v1.register('favorites', FavoriteViewSet, basename='favorite')
router_v1.register('purchases', BasketViewSet, basename='basket')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
