from recipes.const import GIT_HUB, PROJECT_NAME, TAGS
from django.shortcuts import redirect
import re


def tag_from_get(request):

    temp_actual_tags = {}
    for tag in TAGS:
        temp_tag = re.search(rf'{tag}=\d', request.get_full_path())
        if not temp_tag:
            temp_actual_tags[tag] = 1
    return temp_actual_tags


class ActualTagsMiddleware:
    """Add actual tags in request.META."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tags = tag_from_get(request)
        request.META['actual_tags'] = tags
        return self.get_response(request)


class PaginatorMiddleware:
    """Redirect to last_page if non valid paginator."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        page = request.GET.get('page')
        try:
            paginator = response.context_data.get('paginator')
        except AttributeError:
            paginator = None
        if (page and paginator) and (page.isdigit() is False or int(page) > paginator.num_pages):
            q = request.GET.get('q')
            full_path = f'{request.path}?page={paginator.num_pages}'
            if q:
                full_path = f'{full_path}&q={q}'
            return redirect(full_path)
        return response
