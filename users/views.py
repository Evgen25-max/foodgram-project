from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm
from .utils import check_token_and_save

User = get_user_model()


class UserCreationForm(CreateView):
    """Signup."""

    form_class = CustomUserCreationForm
    success_url = reverse_lazy('activate')
    template_name = 'users/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('recipes:index')
        return super().dispatch(request, *args, **kwargs)


def activate_user(request, uid64, token):
    """User activation with a valid uid64 and token."""

    if check_token_and_save(User, uid64, token):
        return redirect('sucess-user-activate')
    return redirect('error-user-activate')
