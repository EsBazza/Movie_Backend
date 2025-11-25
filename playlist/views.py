from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Movie, Playlist, PlaylistItem
from .serializers import (
    MovieSerializer,
    PlaylistSerializer,
    PlaylistListSerializer,
    PlaylistItemSerializer,
    AddMovieToPlaylistSerializer,
    UpdatePlaylistItemStatusSerializer,
)


class MovieViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Movie CRUD operations.
    
    GET /api/movies/ - List all movies
    POST /api/movies/ - Create a movie
    GET /api/movies/{id}/ - Get movie detail
    PUT /api/movies/{id}/ - Update movie
    DELETE /api/movies/{id}/ - Delete movie
    """
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class PlaylistViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Playlist CRUD operations.
    
    GET /api/playlists/ - List all playlists
    POST /api/playlists/ - Create a playlist
    GET /api/playlists/{id}/ - Get playlist detail with movies
    PUT /api/playlists/{id}/ - Update playlist
    DELETE /api/playlists/{id}/ - Delete playlist
    
    Custom Actions:
    POST /api/playlists/{id}/add_movie/ - Add a movie to playlist
    DELETE /api/playlists/{id}/remove_movie/ - Remove a movie from playlist
    PATCH /api/playlists/{id}/update_item_status/ - Update movie status in playlist
    """
    queryset = Playlist.objects.all()

    def get_serializer_class(self):
        """Use lightweight serializer for list view, full serializer for detail."""
        if self.action == "list":
            return PlaylistListSerializer
        return PlaylistSerializer

    @action(detail=True, methods=["post"])
    def add_movie(self, request, pk=None):
        """Add a movie to this playlist."""
        playlist = self.get_object()
        serializer = AddMovieToPlaylistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movie_id = serializer.validated_data["movie_id"]
        status_value = serializer.validated_data["status"]

        movie = get_object_or_404(Movie, pk=movie_id)

        # Check if already in playlist
        if PlaylistItem.objects.filter(playlist=playlist, movie=movie).exists():
            return Response(
                {"error": "Movie already in playlist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item = PlaylistItem.objects.create(
            playlist=playlist,
            movie=movie,
            status=status_value
        )
        return Response(
            PlaylistItemSerializer(item).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["delete"], url_path="remove_movie/(?P<movie_id>[^/.]+)")
    def remove_movie(self, request, pk=None, movie_id=None):
        """Remove a movie from this playlist."""
        playlist = self.get_object()
        item = get_object_or_404(PlaylistItem, playlist=playlist, movie_id=movie_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="update_item_status/(?P<movie_id>[^/.]+)")
    def update_item_status(self, request, pk=None, movie_id=None):
        """Update a movie's watch status in this playlist."""
        playlist = self.get_object()
        item = get_object_or_404(PlaylistItem, playlist=playlist, movie_id=movie_id)

        serializer = UpdatePlaylistItemStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item.status = serializer.validated_data["status"]
        item.save()

        return Response(PlaylistItemSerializer(item).data)


class PlaylistItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for PlaylistItem CRUD operations.
    Useful for directly managing items without going through playlist.
    
    GET /api/playlist-items/ - List all items
    GET /api/playlist-items/{id}/ - Get item detail
    PATCH /api/playlist-items/{id}/ - Update item (e.g., change status)
    DELETE /api/playlist-items/{id}/ - Remove item
    """
    queryset = PlaylistItem.objects.select_related("movie", "playlist").all()
    serializer_class = PlaylistItemSerializer

