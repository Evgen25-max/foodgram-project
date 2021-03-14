from django.contrib import admin

from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    """Configuring the Recipe model for the admin panel."""

    list_display = (
        'pk',
        'email',
        'first_name',
        'last_name',
        'username',
        'pub_date',
        'admin',
    )
    search_fields = ('email', 'username')
    empty_value_display = '-empty-'


admin.site.register(CustomUser)
