# Generated by Django 2.2.28 on 2023-02-27 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230226_1632'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={
                'verbose_name': 'рецепт - ингредиент',
                'verbose_name_plural': 'рецепты - ингредиенты'
            },
        ),
        migrations.AlterModelOptions(
            name='tagrecipe',
            options={
                'verbose_name': 'рецепт - тег',
                'verbose_name_plural': 'рецепты - теги'
            },
        ),
    ]
