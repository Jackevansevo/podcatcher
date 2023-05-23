from django.urls import path

from . import views

urlpatterns = [
    path("", views.SubscriptionListView.as_view(), name="subscription-list"),
    path("search", views.search, name="search"),
    path("subscribe", views.subscribe, name="subscribe"),
    path("unsubscribe", views.unsubscribe, name="unsubscribe"),
    path("favourite/<uuid:pk>", views.favourite, name="favourite"),
    path("unfavourite/<uuid:pk>", views.unfavourite, name="unfavourite"),
    path("episodes", views.EpisodeListView.as_view(), name="episode-list"),
    path(
        "episodes/favourites",
        views.EpisodeFavouriteView.as_view(),
        name="episode-favourites",
    ),
    path(
        "episodes/listening",
        views.EpisodeListeningView.as_view(),
        name="episode-listening",
    ),
    path("podcast/<uuid:pk>", views.podcast_detail_view, name="podcast-detail"),
]
