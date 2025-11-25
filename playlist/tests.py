from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Movie, Playlist, PlaylistItem


class MovieModelTests(TestCase):
    def test_movie_str(self):
        movie = Movie.objects.create(title="Inception", release_year=2010)
        self.assertEqual(str(movie), "Inception (2010)")

    def test_movie_without_year(self):
        movie = Movie.objects.create(title="Unknown Movie")
        self.assertEqual(str(movie), "Unknown Movie (N/A)")


class PlaylistModelTests(TestCase):
    def test_playlist_str(self):
        playlist = Playlist.objects.create(title="My Watchlist")
        self.assertEqual(str(playlist), "My Watchlist")

    def test_playlist_progress(self):
        playlist = Playlist.objects.create(title="Test List")
        m1 = Movie.objects.create(title="Movie 1")
        m2 = Movie.objects.create(title="Movie 2")
        m3 = Movie.objects.create(title="Movie 3")

        PlaylistItem.objects.create(playlist=playlist, movie=m1, status=PlaylistItem.Status.WATCHED)
        PlaylistItem.objects.create(playlist=playlist, movie=m2, status=PlaylistItem.Status.WATCHED)
        PlaylistItem.objects.create(playlist=playlist, movie=m3, status=PlaylistItem.Status.TO_WATCH)

        watched, total = playlist.get_progress()
        self.assertEqual(watched, 2)
        self.assertEqual(total, 3)


class PlaylistAPITests(APITestCase):
    def setUp(self):
        self.playlist = Playlist.objects.create(
            title="Horror Movies",
            description="Scary stuff"
        )
        self.movie = Movie.objects.create(
            title="The Shining",
            release_year=1980
        )

    def test_list_playlists(self):
        """GET /api/playlists/ should return list of playlists."""
        response = self.client.get("/api/playlists/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_playlist(self):
        """POST /api/playlists/ should create a new playlist."""
        data = {"title": "New Playlist", "description": "Test"}
        response = self.client.post("/api/playlists/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Playlist.objects.count(), 2)

    def test_get_playlist_detail(self):
        """GET /api/playlists/{id}/ should return playlist with items."""
        response = self.client.get(f"/api/playlists/{self.playlist.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Horror Movies")

    def test_update_playlist(self):
        """PUT /api/playlists/{id}/ should update the playlist."""
        data = {"title": "Updated Title", "description": "New desc"}
        response = self.client.put(f"/api/playlists/{self.playlist.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.playlist.refresh_from_db()
        self.assertEqual(self.playlist.title, "Updated Title")

    def test_delete_playlist(self):
        """DELETE /api/playlists/{id}/ should delete the playlist."""
        response = self.client.delete(f"/api/playlists/{self.playlist.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Playlist.objects.count(), 0)

    def test_add_movie_to_playlist(self):
        """POST /api/playlists/{id}/add_movie/ should add a movie."""
        data = {"movie_id": self.movie.id, "status": "to_watch"}
        response = self.client.post(
            f"/api/playlists/{self.playlist.id}/add_movie/",
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.playlist.items.count(), 1)

    def test_update_item_status(self):
        """PATCH should update movie status in playlist."""
        PlaylistItem.objects.create(
            playlist=self.playlist,
            movie=self.movie,
            status=PlaylistItem.Status.TO_WATCH
        )
        response = self.client.patch(
            f"/api/playlists/{self.playlist.id}/update_item_status/{self.movie.id}/",
            {"status": "watched"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = PlaylistItem.objects.get(playlist=self.playlist, movie=self.movie)
        self.assertEqual(item.status, PlaylistItem.Status.WATCHED)


class MovieAPITests(APITestCase):
    def test_create_movie(self):
        """POST /api/movies/ should create a movie."""
        data = {
            "title": "Interstellar",
            "poster_url": "https://example.com/poster.jpg",
            "description": "Space movie",
            "release_year": 2014
        }
        response = self.client.post("/api/movies/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 1)

    def test_list_movies(self):
        """GET /api/movies/ should list all movies."""
        Movie.objects.create(title="Movie 1")
        Movie.objects.create(title="Movie 2")
        response = self.client.get("/api/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

