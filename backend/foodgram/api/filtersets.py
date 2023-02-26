from django_filters import ModelMultipleChoiceFilter, FilterSet
from recipes.models import Recipe, Tag


class TitleFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

