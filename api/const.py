from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import AuthorOnly, IsFollower

CATEGORIE_METHOD_PERMISSIONS = {
    'POST': (IsAuthenticated,),
    'DELETE': (IsFollower,),
}

FAVORITE_METHOD_PERMISSIONS = {
    'POST': (IsAuthenticated,),
    'DELETE': (AuthorOnly,),
}

BASKET_USER_METHOD_PERMISSIONS = {
    'POST': (AllowAny,),
    'DELETE': (AllowAny,),
}

SUBSCRIPTION_USER_METHOD_PERMISSIONS = {
    'POST': (IsAuthenticated,),
    'DELETE': (AuthorOnly,),
}
