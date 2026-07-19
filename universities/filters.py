import django_filters

from .models import University


class UniversityFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(field_name="state__name", lookup_expr="iexact")
    city = django_filters.CharFilter(field_name="city__name", lookup_expr="iexact")
    featured = django_filters.BooleanFilter(field_name="is_featured")
    type = django_filters.CharFilter(field_name="university_type", lookup_expr="iexact")
    ranking = django_filters.CharFilter(field_name="ranking_tier", lookup_expr="iexact")

    class Meta:
        model = University
        fields = ["state", "city", "featured", "type", "ranking"]
