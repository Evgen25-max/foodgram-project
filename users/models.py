from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utils import mas_send, sent_email_activate


class CustomUserManager(BaseUserManager):
    """Sending emails with a link to activate when creating users in bulk."""

    def bulk_create(self, objs):
        new_users = super().bulk_create(objs)
        all_new_user = CustomUser.objects.filter(username__in=[a1.username for a1 in new_users])
        rezult_send = mas_send(all_new_user)
        all_new_user.filter(username__in=[rezult for rezult in rezult_send if rezult is not None])
        for new_user in all_new_user:
            new_user.email_send = True
        CustomUser.objects.bulk_update(all_new_user, ['email_send'])


class CustomUser(AbstractUser):
    email_send = models.BooleanField(default=False)
    email = models.EmailField(blank=True, unique=True)
    is_active = models.BooleanField(default=False,)

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            rezult_send = sent_email_activate(self)
            if rezult_send:
                self.email_send = True
                super().save()
        else:
            super().save(*args, **kwargs)


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
