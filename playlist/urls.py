from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, PlaylistViewSet, PlaylistItemViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"playlists", PlaylistViewSet, basename="playlist")
router.register(r"playlist-items", PlaylistItemViewSet, basename="playlistitem")

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
