from django.urls import path

from .views import (
    AlertDeleteView,
    AlertDetailView,
    AlertListView,
    AlertMarkAllAsReadView,
    AlertMarkAsReadView,
)

urlpatterns = [
    path("", AlertListView.as_view(), name="alert-list"),
    path("<int:pk>/", AlertDetailView.as_view(), name="alert-detail"),
    path("<int:pk>/read/", AlertMarkAsReadView.as_view(), name="alert-mark-read"),
    path("read-all/", AlertMarkAllAsReadView.as_view(), name="alert-mark-all-read"),
    path("<int:pk>/delete/", AlertDeleteView.as_view(), name="alert-delete"),
]
