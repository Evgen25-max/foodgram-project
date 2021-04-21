import re

from django.shortcuts import redirect

from recipes.const import TAGS_DATA


def tag_from_get(path):
    count_active_tag = 0
    temp_actual_tags = {}
    for tag in TAGS_DATA:
        temp_tag = re.search(rf'{tag}=\d', path)
        if temp_tag and temp_tag[0][-1] == '0':
            temp_actual_tags[tag] = 0
        else:
            temp_actual_tags[tag] = 1
            count_active_tag += 1

    return temp_actual_tags, count_active_tag


def get_tags_urls_colors_rus(tags, view_path):
    all_data_tags = {}

    for tag in tags:
        temp_url = ''.join([f'{i}={tags[i]}' if i != tag else f'{i}={1 - tags[i]}' for i in tags])
        all_data_tags.update({tag: [tags[tag], TAGS_DATA[tag][0], f'{view_path}?&q={temp_url}', TAGS_DATA[tag][1]]})
    return all_data_tags


class ActualTagsMiddleware:
    """Add actual tags in request.META."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        The tag data is added to request.meta.

        Output data format: {
        str: tag title:  [
            int: True/False tag is active,
            str: russian title tag,
            str: link to jump when clicking on a tag,
            str: tag color
            ]
        }
        """

        tags, count_active_tag = tag_from_get(request.get_full_path())
        tags_data = get_tags_urls_colors_rus(tags, request.path)
        request.META['actual_tags'] = tags_data
        request.META['count_tags'] = count_active_tag
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
