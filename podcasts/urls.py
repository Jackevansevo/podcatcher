from django.urls import path

from . import views

urlpatterns = [
    path("", views.PodcastListView.as_view(), name="podcast-list"),
    path("search", views.search, name="search"),
    path("import-feed", views.import_feed, name="import-feed"),
    path("podcast/<uuid:pk>", views.PodcastDetailView.as_view(), name="podcast-detail"),
]
