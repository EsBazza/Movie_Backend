from django.conf import settings
from django.db import models
from django.utils import timezone


class Movie(models.Model):
    """Movie model - stores movie info (can be manually added or fetched from TMDB)."""

    title = models.CharField(max_length=512)
    poster_url = models.URLField(max_length=1024, blank=True, null=True)
    description = models.TextField(blank=True, default="")
    release_year = models.PositiveIntegerField(blank=True, null=True)
    # TMDB integration fields
    tmdb_id = models.IntegerField(blank=True, null=True, unique=True, db_index=True)
    youtube_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.release_year or 'N/A'})"


class Playlist(models.Model):
    """Playlist/Watchlist - core CRUD entity for the mobile app."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    movies = models.ManyToManyField(
        Movie,
        through="PlaylistItem",
        related_name="playlists",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def movie_count(self) -> int:
        return self.items.count()

    @property
    def watched_count(self) -> int:
        return self.items.filter(status=PlaylistItem.Status.WATCHED).count()

    def get_progress(self):
        """Returns (watched, total) tuple for progress tracking."""
        total = self.items.count()
        watched = self.items.filter(status=PlaylistItem.Status.WATCHED).count()
        return watched, total


class PlaylistItem(models.Model):
    """Through model linking Movie <-> Playlist with watch status."""

    class Status(models.TextChoices):
        TO_WATCH = "to_watch", "To Watch"
        WATCHING = "watching", "Watching"
        WATCHED = "watched", "Watched"

    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name="items"
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="playlist_items"
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.TO_WATCH
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("playlist", "movie")
        ordering = ["-added_at"]

    def __str__(self) -> str:
        return f"{self.movie.title} in {self.playlist.title} ({self.get_status_display()})"

