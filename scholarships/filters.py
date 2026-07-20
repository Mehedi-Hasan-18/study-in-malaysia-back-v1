import django_filters

from .models import Scholarship


class ScholarshipFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(field_name="eligible_country", lookup_expr="iexact")
    coverage = django_filters.NumberFilter(field_name="coverage_percentage")
    level = django_filters.CharFilter(method="filter_level")
    deadline_before = django_filters.DateFilter(field_name="application_deadline", lookup_expr="lte")

    class Meta:
        model = Scholarship
        fields = ["country", "coverage", "level", "university", "deadline_before"]

    def filter_level(self, queryset, name, value):
        return queryset.filter(eligible_level__contains=[value])
