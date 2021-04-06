from django.db import models
from django.utils.translation import gettext_lazy as _


class TAG_RECIPE(models.TextChoices):
    '''--'''

    BREAKFAST = 'breakfast', _('Завтрак')
    LUNCH = 'lunch', _('Обед')
    DINNER = 'dinner', _('Ужин')


TAG_RUS = {
    'breakfast': 'Завтрак',
    'lunch': 'Обед',
    'dinner': 'Ужин',
}

TAG_COLOR = {
    'breakfast': 'green',
    'lunch': 'orange',
    'dinner': 'purple',
}


PROJECT_NAME = 'Foodgram_project'
GIT_HUB = 'https://github.com/Evgen25-max'

TAGS = ['breakfast', 'lunch', 'dinner']
