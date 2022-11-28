import os
import requests
from pytube import YouTube
from spotdl import Spotdl

spotdl = Spotdl(client_id=os.environ['CLIENT-ID'], client_secret= os.environ['CLIENT-SCRT'])

def buscar(query):
  response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={ os.environ['GOOGLE-API'] }&part=snippet&q={ query }&maxResults=3&categories=Music")

  res = response.json()
  song = res['items'][0]['snippet']
  song_title = song['title']
  song_autor = song['channelTitle']
  song_id = res['items'][0]['id']['videoId']
  song_url = f'youtube.com/watch?v={ song_id }'
  return song_title, song_url


def descarga(url):
  song = YouTube(url)
  try:
    streams = song.streams.filter(type='audio', audio_codec='opus').order_by('abr')
    
  except:
    streams = song.streams.filter(type='audio').order_by('abr')  
  finally: 
    file = streams.last().download()
    print( streams
         )
    file_title = song.title
    file_author = song.author
    
    print(file)
    print(song)

  return file, file_title, file_author

def nuevadescarga(query):
	songs = spotdl.search([query])
	# results = spotdl.download_songs(songs)
	song, path = spotdl.download(songs[0])
	print(path)
	return path

