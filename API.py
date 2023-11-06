import os
import requests
from pytube import YouTube
from spotdl import Spotdl
import json

spotdl = Spotdl(
    client_id=os.environ["CLIENTID"], client_secret=os.environ["CLIENTSCRT"]
)


def spotauthentication():
    CLIENT_ID = os.environ["CLIENTID"]
    CLIENT_SECRET = os.environ["CLIENTSCRT"]

    grant_type = "client_credentials"
    body_params = {"grant_type": grant_type}

    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, data=body_params, auth=(CLIENT_ID, CLIENT_SECRET))

    token_raw = json.loads(response.text)
    token = token_raw["access_token"]
    print(token)
    return token


token = spotauthentication()


def buscar(query):
    response = requests.get(
        f"https://www.googleapis.com/youtube/v3/search?key={ os.environ['GOOGLEAPI'] }&part=snippet&q={ query }&maxResults=3&categories=Music"
    )

    res = response.json()
    song = res["items"][0]["snippet"]
    song_title = song["title"]
    song_autor = song["channelTitle"]
    song_id = res["items"][0]["id"]["videoId"]
    song_url = f"youtube.com/watch?v={ song_id }"
    return song_title, song_url


def search_album(album_name):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": album_name, "type": "album", "limit": 1}
    response = requests.get(
        "https://api.spotify.com/v1/search", headers=headers, params=params
    )
    res = response.json()
    album = res["albums"]["items"][0]
    album_name = album["name"]
    album_url = album["external_urls"]["spotify"]
    return album_url


def descargayoutube(url, type):
    letype = type
    song = YouTube(url)
    streams = None
    try:
        if type == "audio":
            streams = song.streams.filter(only_audio=True).first()
        elif type == "video":
            streams = song.streams.filter(file_extension="mp4").order_by("res").last()
    except:
        streams = song.streams.filter(only_audio=True).order_by("abr").last()
    finally:
        print(streams)
        file = streams.download()
        file_title = song.title
        file_author = song.author

        print(file)
        print(song)
    return file


def nuevadescarga(songg, playlist: bool = False):
    if playlist:
        results = spotdl.download_songs(songg)
        print("Pasa por aca0")
        return results
    else:
        song, path = spotdl.download(songg)
        print("Pasa por aca0")
        print(song)
        return song, path


def nuevabusqueda(query, playlist: bool = False):
    songs = spotdl.search([query])
    print(songs[0])
    if playlist:
        return songs
    else:
        return songs[0]


def getrecomendaciones(songs, genres, artist):
    songss = ",".join(songs)
    genress = ",".join(genres)
    artistss = ",".join(artist)

    response = requests.get(
        "https://api.spotify.com/v1/recommendations",
        params={
            "seed_tracks": songss,
            "seed_artists": artistss,
            "seed_genres": genress,
            "limit": "1",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    res = response.json()
    print(res["tracks"][0]["href"])
    url = "https://open.spotify.com/track/" + res["tracks"][0]["id"]
    return url


def detectsong(urlofsong):
    url = "https://shazam-api7.p.rapidapi.com/songs/recognize-song"

    files = {"audio": open(urlofsong, "rb")}
    print(files)
    headers = {
        "X-RapidAPI-Key": "9f0f33e040mshdde222da854c370p160e02jsn4f671dffc290",
        "X-RapidAPI-Host": "shazam-api7.p.rapidapi.com",
    }
    try:
        response = requests.post(url, files=files, headers=headers).json()
        print(response)
        song = {
            "artist": response["track"]["subtitle"],
            "name": response["track"]["title"],
            "album": " ",
            "url": response["track"]["url"],
            "image": response["track"]["images"]["coverart"],
        }
        print(song)
        return song
    except:
        print("No se se encontro la cancion")
        return "nope"


# getrecomendaciones(['0tfNpwQTfHuBvv2jQESnaR'], ['pop', 'dance pop'],[''])
