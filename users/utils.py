import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

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


def sent_email_activate(user, rezult_send=None):
    """Sends an email with a link to activate the user."""

    activate_token = account_activation_token.make_token(user)
    uid64 = urlsafe_base64_encode(force_bytes(user))
    site = Site.objects.get(id=settings.SITE_ID)
    activate_url = reverse('auth: activate', kwargs={'uid64': uid64, 'token': activate_token})
    user_email = user.email
    answer_send = send_mail(
        subject=EMAIL['MESSAGE_SUBJ_SIGN_UP'],
        message=f"{EMAIL['MESSAGE_SIGN_UP']}{EMAIL['PROTOCOL']}://{site.domain}{activate_url}",
        from_email=None,
        recipient_list=[user_email],
    )
    if rezult_send is not None:
        rezult_send[user.username] = answer_send
        return rezult_send
    return answer_send


def check_token_and_save(user_model, uid64, activation_token):
    """Checking the validity of the token and uid64."""

    uid = force_text(urlsafe_base64_decode(uid64))
    activate_user = get_object_or_404(user_model.objects.filter(username=uid))
    if account_activation_token.check_token(activate_user, activation_token):
        activate_user.is_active = True
        activate_user.save()
        return True
    return False


def mas_send(users):
    """Bulk email distribution with links to activate users."""

    async def send_many():

        futures = [loop.run_in_executor(executor, sent_email_activate, user, rezult_send) for user in users]
        await asyncio.gather(*futures)

    rezult_send = defaultdict()
    executor = ThreadPoolExecutor(max_workers=len(users))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_many())
    return rezult_send
