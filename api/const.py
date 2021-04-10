from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import AuthorOnly, IsFollower
from recipes.models import Favorite, BasketUser


METHOD_PERMISSIONS = {
    'basket': {
        'POST': (AllowAny,),
        'DELETE': (AllowAny,),
    },
    'subscriptions': {
        'POST': (IsAuthenticated,),
        'DELETE': (AuthorOnly,),
    },
    'favorite': {
        'POST': (IsAuthenticated,),
        'DELETE': (AuthorOnly,),
    }
}