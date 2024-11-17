import unittest
import API
from unittest.mock import patch

# import icecream as ic


class TestAPI(unittest.TestCase):
    def test_search_album(self):
        # Replace 'test_album' with the name of an album that exists
        album_url = API.search_album("LSD Labrinth, Sia & Diplo ")
        print(album_url)
        # Replace 'expected_url' with the expected Spotify URL of the album
        expected_url = "https://open.spotify.com/album/0ujHQ5WCLuKJQXOqXpGtpf"
        self.assertEqual(album_url, expected_url)

    @patch("requests.get")
    def test_search_youtube(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            "items": [
                {
                    "snippet": {"title": "Test Song", "channelTitle": "Test Channel"},
                    "id": {"videoId": "test123"},
                }
            ]
        }

        song_title, song_url = API.search_youtube("Boy In Space Alan Walker")

        self.assertEqual(song_title, "Test Song")
        self.assertEqual(song_url, "youtube.com/watch?v=test123")


if __name__ == "__main__":
    unittest.main()
