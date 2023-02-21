# Generated by Django 2.2.28 on 2023-02-20 17:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactions_with_recipes', '0003_auto_20230220_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_users', to='recipes.Recipe', verbose_name='рецепт'),
        ),
        migrations.AlterUniqueTogether(
            name='favorites',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='favorites',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='favorites_user_recipe_unique'),
        ),
    ]