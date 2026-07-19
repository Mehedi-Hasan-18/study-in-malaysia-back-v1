from rest_framework import viewsets

from .models import City, Country, State
from .serializers import CitySerializer, CountrySerializer, StateSerializer


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all().order_by("name")
    serializer_class = CountrySerializer
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.select_related("country").all().order_by("name")
    serializer_class = StateSerializer
    filterset_fields = ["country"]
    search_fields = ["name"]
    ordering_fields = ["name"]


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.select_related("state", "state__country").all().order_by("name")
    serializer_class = CitySerializer
    filterset_fields = ["state", "state__country"]
    search_fields = ["name"]
    ordering_fields = ["name"]
