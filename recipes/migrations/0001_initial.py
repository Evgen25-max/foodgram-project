# Generated by Django 3.0.5 on 2021-03-16 16:06

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Enter the title of the ingredient.', max_length=200, verbose_name='the title of the ingredient')),
                ('dimension', models.CharField(help_text='dimension for ingredient', max_length=10, verbose_name='the unit of measurement of the ingredient')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Enter the title of the recipe', max_length=100, verbose_name='the title of the recipe')),
                ('image', models.ImageField(blank=True, default='recipes/defaultImage.png', help_text='Upload a recipe image', null=True, upload_to='recipes/', verbose_name='image for recipe')),
                ('description', models.TextField(blank=True, help_text='write a description of the recipe', null=True, verbose_name='Description of recipe')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='enter the cooking time in minutes', verbose_name='cooking time')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='publication date')),
            ],
            options={
                'verbose_name': 'recipe',
                'verbose_name_plural': 'recipes',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_time', models.CharField(choices=[('breakfast', 'Завтрак'), ('lunch', 'Обед'), ('dinner', 'Ужин')], max_length=20, unique=True, verbose_name='meal for time')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(help_text='input amount for ingredient', validators=[django.core.validators.MinValueValidator(0, 'значение должно быть больше 0')], verbose_name='quantity of ingredient')),
                ('ingredient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.Recipe')),
            ],
            options={
                'verbose_name': 'Ingredient for recipe',
                'verbose_name_plural': 'Ingredients for recipe',
            },
        ),
    ]
