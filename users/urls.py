from django.urls import path

from . import views

app_name = 'auth'
urlpatterns = [
    path('signup/', views.UserCreationForm.as_view(), name='signup'),
    path('activate/<str:uid64>/<str:token>/', views.activate_user, name=' activate'),
]
