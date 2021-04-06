from django.urls import path

from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('new/', views.NewRecipe.as_view(), name='new_recipe'),
    path('subscriptions/', views.SubscriptionRecipe.as_view(), name='subscriptions'),
    path('shoplist/', views.ShopList.as_view(), name='shoplist'),
    path('shoplist/file/', views.shoplist_file, name='shoplist_file'),
    path('recipes/<str:username>/', views.ProfileUser.as_view(), name='profile'),

    path('recipes/<str:username>/favorite/', views.FavoriteRecipe.as_view(), name='favorite'),
    path('recipes/<str:username>/<int:recipe_id>/', views.RecipeView.as_view(), name='recipe'),
    path('recipes/<str:username>/<int:pk>/remove/', views.RecipeDelete.as_view(), name='remove_recipe'),
    path('recipes/<str:username>/<int:recipe_id>/edit/', views.RecipeUpdate.as_view(), name='recipe_edit'),

]
