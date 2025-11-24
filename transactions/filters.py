import django_filters
from .models import Transaction
from django.db import models


class TransactionFilter(django_filters.FilterSet):
    # Buscar por texto (name o description)
    search = django_filters.CharFilter(method="filter_search", label="Text search")

    # Filtrar por rango de fechas
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    # Filtrar por cuenta
    origin_account = django_filters.NumberFilter(field_name="origin_account__id")
    destination_account = django_filters.NumberFilter(field_name="destination_account__id")

    class Meta:
        model = Transaction
        fields = ["type", "origin_account", "destination_account"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(tag__icontains=value)
        )
