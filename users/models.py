from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import account_activation_token, sent_email_activate


class CustomUser(AbstractUser):
    admin = models.BooleanField(default=False)
    email = models.EmailField(blank=True, unique=True)
    is_active = models.BooleanField(default=False,)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        sent_email_activate(self, account_activation_token)


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
