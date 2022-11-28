# Music Downloader Bot

Telegram bot made with the python, for unique purpose of downloading songs high quality songs with all the metada from the internet.
You can use this bot clicking here [MusicBot](https://t.me/downspotmusicbot) or searching for @**downspotmusicbot** in telegram

## Dependencies
- Requests: Making the requests to youtube API for searching songs, and for the Spotify recommendations API
- Python-telegram-bot: As the core library for building the telegram bot
- Pytube: To download the songs from youtube
- Spotdl: To download songs with the spotify links and search engine, but downloading the songs from YoutubeMusic

It may seem that there is a bit of redundacy with dependencie modules and it's true. I am migrating all the critical operations to Spotdl api.

## Building
### Docker
Buildit with docker using the Dockerfile and setting the environment variable

### Poetry
You can buildit from the source code using poetry
#### Install Poetry:
~~~ sh
	sudo apt-get upgrade && sudo apt-get update && sudo apt-get install poetry
~~~

#### Install Dependencies:
~~~ sh
	poetry install
~~~

Install **ffmpeg**:
~~~ 
	sudo apt-get install -y ffmpeg
~~~
#### Set The Env Variables
~~~ sh
	BOT-TOKEN = # The telegram bot token
	GOOGLE-API = # GoogleAPiToken
    CLIENT-ID = # Spotify CLient Id
    CLIENT-SCRT = # Spotify Client Secret
~~~

#### Run The Project
~~~ sh
	poetry run python3.8 main.py
~~~

