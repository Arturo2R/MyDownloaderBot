import unittest
import API

# import icecream as ic


class TestAPI(unittest.TestCase):
    def test_search_album(self):
        # Replace 'test_album' with the name of an album that exists
        album_url = API.search_album("LSD Labrinth, Sia & Diplo ")
        print(album_url)
        # Replace 'expected_url' with the expected Spotify URL of the album
        expected_url = "https://open.spotify.com/album/0ujHQ5WCLuKJQXOqXpGtpf"
        self.assertEqual(album_url, expected_url)


if __name__ == "__main__":
    unittest.main()
