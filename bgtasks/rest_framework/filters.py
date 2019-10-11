import django_filters


class DefaultFilterSet(django_filters.FilterSet):
    ids = django_filters.NumberFilter(method='filter_by_ids')

    def filter_by_ids(self, queryset, name, value):
        return queryset.filter(id__in=value)
