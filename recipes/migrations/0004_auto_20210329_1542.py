# Generated by Django 3.0 on 2021-03-29 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipetag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipetag',
            name='meal_time',
            field=models.CharField(choices=[('Завтрак', 'Breakfast'), ('Обед', 'Lunch'), ('Ужин', 'Dinner')], max_length=20, unique=True, verbose_name='meal for time'),
        ),
    ]
