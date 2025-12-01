import django_filters
from .models import Transaction
from django.db import models


class TransactionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Text search")

    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    origin_account = django_filters.NumberFilter(field_name="origin_account__id")
    destination_account = django_filters.NumberFilter(field_name="destination_account__id")
    category = django_filters.NumberFilter(field_name="category__id")

    class Meta:
        model = Transaction
        fields = ["type", "origin_account", "destination_account", "category"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(tag__icontains=value)
            | models.Q(description__icontains=value)
            | models.Q(note__icontains=value)
            | models.Q(category__name__icontains=value)
        )
