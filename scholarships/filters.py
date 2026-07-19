import django_filters

from .models import Scholarship


class ScholarshipFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(field_name="eligible_country", lookup_expr="iexact")
    coverage = django_filters.NumberFilter(field_name="coverage_percentage")
    level = django_filters.CharFilter(field_name="eligible_level", lookup_expr="iexact")
    deadline_before = django_filters.DateFilter(field_name="application_deadline", lookup_expr="lte")

    class Meta:
        model = Scholarship
        fields = ["country", "coverage", "level", "university", "deadline_before"]
