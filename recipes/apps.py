import os

from django.apps import AppConfig
from django.conf import settings
from reportlab.pdfbase import pdfmetrics, ttfonts


class RecipesConfig(AppConfig):
    """Representing Recipes application with registration fonts for PDF files."""

    name = 'recipes'

    def ready(self):
        Font_FreeSans = ttfonts.TTFont(
            'FreeSans', os.path.join(settings.BASE_DIR, 'recipes/static/fonts/FreeSans.ttf')
        )
        Font_FreeSansOblique = ttfonts.TTFont(
            'FreeSansOblique', os.path.join(settings.BASE_DIR, 'recipes/static/fonts/FreeSansOblique.ttf')
        )
        pdfmetrics.registerFont(Font_FreeSans)
        pdfmetrics.registerFont(Font_FreeSansOblique)
