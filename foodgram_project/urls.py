from django.conf import settings
from django.conf.urls import handler404, handler500  # noqa
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about-author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='about-spec'),
    path('sucess-activate/', views.flatpage, {'url': '/sucess-activate/'}, name='sucess-user-activate'),
    path('error-activate/', views.flatpage, {'url': '/error-activate/'}, name='error-user-activate'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='about-spec'),
    path('api/', include('api.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('users.urls')),

    path('', include('recipes.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
handler404 = 'recipes.views.page_not_found' # noqa
handler500 = 'recipes.views.server_error' # noqa