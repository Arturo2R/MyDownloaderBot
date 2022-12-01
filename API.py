import os
import requests
from pytube import YouTube
from spotdl import Spotdl
import json

spotdl = Spotdl(client_id=os.environ['CLIENTID'], client_secret= os.environ['CLIENTSCRT'])

def spotauthentication():
	CLIENT_ID = os.environ['CLIENTID']
	CLIENT_SECRET = os.environ['CLIENTSCRT']
	
	grant_type = 'client_credentials'
	body_params = {'grant_type' : grant_type}
	
	url='https://accounts.spotify.com/api/token'
	response = requests.post(url, data=body_params, auth = (CLIENT_ID, CLIENT_SECRET)) 
	
	token_raw = json.loads(response.text)
	token = token_raw["access_token"]
	print(token)
	return token

token = spotauthentication()

def buscar(query):
  response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={ os.environ['GOOGLEAPI'] }&part=snippet&q={ query }&maxResults=3&categories=Music")

  res = response.json()
  song = res['items'][0]['snippet']
  song_title = song['title']
  song_autor = song['channelTitle']
  song_id = res['items'][0]['id']['videoId']
  song_url = f'youtube.com/watch?v={ song_id }'
  return song_title, song_url


def descargayoutube(url):
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

  return file_title, file 

def nuevadescarga(songg):
	# results = spotdl.download_songs(songs)
	song, path = spotdl.download(songg)
	print(song)
	return song, path 

def nuevabusqueda(query):
	songs = spotdl.search([query])
	print(songs[0])
	return songs[0]

nuevabusqueda("Manuel turizo la bacjata")

def getrecomendaciones(songs, genres, artist):
	songss = ','.join(songs)
	genress = ','.join(genres)
	artistss = ','.join(artist)
	
	response = requests.get(
		"https://api.spotify.com/v1/recommendations", 
		params={ 
			'seed_tracks': songss, 
			'seed_artists': artistss, 
			'seed_genres': genress,
			'limit': "1",
		},
		headers= {
			'Authorization': f"Bearer {token}", 
		}
	)
	res = response.json()
	print(res['tracks'][0]['href'])
	url = "https://open.spotify.com/track/" + res['tracks'][0]['id']
	return url
	


def detectsong(urlofsong):
	try:
		response = requests.get(
			"https://api.audd.io/", 
			params={ 
				'api_token': os.environ['AUDDTOKEN'], 
				'url': urlofsong,
				'return': 'spotify'
			},
		)
		res = response.json()
		song = {
			'artist': res['result']['spotify']['artists'][0]['name'],
			'name': res['result']['spotify']['name'],
			'album': res['result']['spotify']['album']['name'],
			'url': res['result']['spotify']['external_urls']['spotify'],
			'image':  res['result']['spotify']['album']['images'][0]
		}
		print(song)
		return song
	except:
		print("No se se encontro la cancion")
		return "nope"
# getrecomendaciones(['0tfNpwQTfHuBvv2jQESnaR'], ['pop', 'dance pop'],[''])
	

