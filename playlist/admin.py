from django.contrib import admin
from .models import Movie, Playlist, PlaylistItem


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "release_year", "created_at")
    search_fields = ("title",)
    list_filter = ("release_year",)
    ordering = ("-created_at",)


class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem
    extra = 1
    autocomplete_fields = ("movie",)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "movie_count", "watched_count", "created_at")
    search_fields = ("title",)
    inlines = [PlaylistItemInline]
    ordering = ("-updated_at",)


@admin.register(PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "playlist", "movie", "status", "added_at")
    list_filter = ("status", "playlist")
    autocomplete_fields = ("movie", "playlist")
