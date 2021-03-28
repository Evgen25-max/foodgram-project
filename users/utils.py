from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .const import EMAIL

account_activation_token = PasswordResetTokenGenerator()


def sent_email_activate(user, account_activation_token):

    activate_token = account_activation_token.make_token(user)
    uid64 = urlsafe_base64_encode(force_bytes(user.pk))
    site = Site.objects.get(id=settings.SITE_ID)
    activate_url = reverse('auth: activate', kwargs={'uid64': uid64, 'token': activate_token})
    user_email = user.email
    send_mail(
        subject=EMAIL['MESSAGE_SUBJ_SIGN_UP'],
        message=f"{EMAIL['PROTOCOL']}://{site.domain}{activate_url}",
        from_email=None,
        recipient_list=[user_email],
    )


def check_token_and_save(user_model, uid, activation_token):

    uid = force_text(urlsafe_base64_decode(uid))
    activate_user = get_object_or_404(user_model.objects.filter(pk=uid))
    if account_activation_token.check_token(activate_user, activation_token):
        activate_user.is_active = True
        activate_user.save()
        return True
    return False
