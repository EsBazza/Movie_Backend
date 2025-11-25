from rest_framework import serializers
from .models import Movie, Playlist, PlaylistItem


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model - used for CRUD operations."""

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "poster_url",
            "description",
            "release_year",
            "tmdb_id",
            "youtube_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PlaylistItemSerializer(serializers.ModelSerializer):
    """Serializer for PlaylistItem - includes nested movie data."""

    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source="movie",
        write_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    class Meta:
        model = PlaylistItem
        fields = [
            "id",
            "movie",
            "movie_id",
            "status",
            "status_display",
            "added_at",
            "updated_at",
        ]
        read_only_fields = ["id", "added_at", "updated_at"]


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for Playlist - the main CRUD entity for the mobile app."""

    items = PlaylistItemSerializer(many=True, read_only=True)
    movie_count = serializers.IntegerField(read_only=True)
    watched_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Playlist
        fields = [
            "id",
            "title",
            "description",
            "movie_count",
            "watched_count",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "movie_count", "watched_count"]


class PlaylistListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing playlists (without nested items)."""

    movie_count = serializers.IntegerField(read_only=True)
    watched_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Playlist
        fields = [
            "id",
            "title",
            "description",
            "movie_count",
            "watched_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AddMovieToPlaylistSerializer(serializers.Serializer):
    """Serializer for adding a movie to a playlist."""

    movie_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=PlaylistItem.Status.choices,
        default=PlaylistItem.Status.TO_WATCH
    )


class UpdatePlaylistItemStatusSerializer(serializers.Serializer):
    """Serializer for updating a playlist item's status."""

    status = serializers.ChoiceField(choices=PlaylistItem.Status.choices)
