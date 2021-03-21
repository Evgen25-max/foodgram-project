from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    admin = models.BooleanField(default=False)
    email = models.EmailField(blank=True, unique=True)

from recipes.models import Recipe  # noqa


class Subscription(models.Model):
    """A model of selected recipe authors."""

    author = models.ForeignKey(
        CustomUser, null=True, on_delete=models.CASCADE, related_name='following', verbose_name=_('author')
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='follower', verbose_name=_('follower'))

    class Meta:
        ordering = ['-author']
        unique_together = ['author', 'user']
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    def __str__(self):
        return f'{self.user} is subscribed to {self.author}'


class Favorite(models.Model):
    """Model of selected recipes."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_fav')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_fav')

    class Meta:
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f'{self.recipe} is favorites for {self.user}'


class BasketUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='basket_user')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='basket_recipe')

    class Meta:
        unique_together = ['user', 'recipe']
