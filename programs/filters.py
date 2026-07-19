import django_filters

from .models import Program


class ProgramFilter(django_filters.FilterSet):
    duration = django_filters.NumberFilter(field_name="duration_months")
    tuition_max = django_filters.NumberFilter(field_name="tuition_fee_display", lookup_expr="lte")

    class Meta:
        model = Program
        fields = ["level", "university", "faculty", "duration", "tuition_max"]
