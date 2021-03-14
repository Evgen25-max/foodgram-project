from django.urls import path

from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_recipe, name='new_recipe'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('shoplist/', views.shoplist, name='shoplist'),
    path('shoplist/file/', views.shoplist_file, name='shoplist_file'),
    path('recipes/<str:username>/', views.profile, name='profile'),


    path('recipes/<str:username>/favorite/', views.favorite, name='favorite'),
    path('recipes/<str:username>/<int:recipe_id>/', views.recipe_view, name='recipe'),
    path('recipes/<str:username>/<int:recipe_id>/remove', views.recipe_remove, name='remove_recipe'),
    path('recipes/<str:username>/<int:recipe_id>/edit/', views.recipe_edit, name='recipe_edit'),

]
