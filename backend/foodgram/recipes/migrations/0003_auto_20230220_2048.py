# Generated by Django 2.2.28 on 2023-02-20 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230220_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=200, verbose_name='название'),
        ),
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='ingredientrecipe',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='tagrecipe',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'unit_of_measurement'), name='name_unit_of_measurement_unique'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='ingredient_recipe_unique'),
        ),
        migrations.AddConstraint(
            model_name='tagrecipe',
            constraint=models.UniqueConstraint(fields=('tag', 'recipe'), name='tag_recipe_unique'),
        ),
    ]
