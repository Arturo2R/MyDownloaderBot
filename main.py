import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton ,  WebAppInfo,  InputMediaAudio, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup, constants
from API import buscar, descargayoutube, nuevadescarga, getrecomendaciones, detectsong, nuevabusqueda

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

class UserData:
	def __init__(self, chatid, songurl, search, title, username, first, last, mode, songhistory, artisthistory, genres, son):
		self.chatid = chatid
		self.songurl = songurl
		self.search = search
		self.title = title
		self.username = username
		self.name = first + ' ' + last
		self.mode = mode
		self.songhistory = songhistory
		self.artishistory = artisthistory
		self.genres = genres
		self.son = son
		

	def __str__(self):
		return f"user:{self.name} id:{self.chatid} url:{self.songurl} query:{self.search}"

	def download(self, context):
		song, path = descargayoutube(self.songurl)
		print(song, path)
		context.bot.send_audio(chat_id=self.chatid,
						   audio=open(path, 'rb'))
		os.remove(path)



users = {
  "prop": "todo"
}


def checkstate(chat):
	if chat.id in users: 
		print('all okey')
	else:
		users[chat.id] = UserData(chat.id, '', '', '', chat.username, chat.first_name, chat.last_name, 'spotify', [], [], [], "")
	print(users[chat.id])

x = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
escape = lambda s, escapechar, specialchars: "".join(escapechar + c if c in specialchars or c == escapechar else c for c in s)

def mostrartarjeta(update, context, user:UserData, name:str,  source:"spotify"or"youtube", url:str, artist="nope", image="nope", album="nope"):
	#artist=escape(artist, "\\", x)
	#name=escape(name, "\\", x)
	#image=escape(image, "\\", x)
	#album=escape(album, "\\", x)
	#source=escape(source, "\\", x)
	if artist=="nope":
		message = f"Te refieres a {name} \n {url} \n "
	else:
		message = f" {name} {artist} \n album: {album} \n {url} \n "
		user.title = str(name + ' ' +artist)	
	# message = escape(message, "\\", x)
	button = [[InlineKeyboardButton("Descargar", callback_data=f"descargar-{source}-audio")]]
	#if source == "youtube":
		#button.append([InlineKeyboardButton("Descargar Video", callback_data=f"descargar-{source}-video")]) 
	context.bot.send_message(chat_id=update.effective_chat.id,text=message,reply_markup=InlineKeyboardMarkup(button))

def descargar(update, context, id, source, type:"audio"or"video"="audio"):
	tipo = type
	context.bot.send_message(chat_id=id, text="Descargando") 
	if source == "spotify":
		song, path = nuevadescarga(users[id].son)
		if song.song_id not in users[id].songhistory :
			users[id].songhistory.append(song.song_id)
		users[id].genres.extend(song.genres)
	elif source == "youtube":
		path = descargayoutube(users[id].songurl, tipo)

	context.bot.send_audio(chat_id=id, audio=open(path, 'rb'))
	os.remove(path)
	
	

def start(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	context.bot.send_message(
        chat_id=chat.id,
        text=
        f'Hola {chat.first_name} Soy un robot creado por @arturo2r, estoy aqui para descargar musica por ti'
    )


def echo(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	if users[chat.id].mode == 'youtube': 
		# global song_title, song_url
		song_title, song_url = buscar(update.message.text)
		users[chat.id].songurl = song_url
		users[chat.id].title = song_title
		mostrartarjeta(update, context, users[chat.id], source="youtube", url=song_url, name=song_title)
		
	if users[chat.id].mode == 'spotify':
		
		# print(context)
		song = nuevabusqueda(update.message.text)
		
		users[chat.id].songurl = song.url
		users[chat.id].title = song.name
		users[chat.id].son = song
		mostrartarjeta(update, context, users[chat.id], source="spotify", url=song.url, name=song.name, image=song.cover_url, album=song.album_name, artist=song.artist)
		
		
		

#def descargar(update, context):
#	chat = update.effective_chat
#	checkstate(chat)
	
#	context.bot.send_message(chat_id=chat.id,
#							 text=f'Descargando {users[chat.id].title}')
#	users[chat.id].download(context)

def spotifymode(update, context):
	print("spot")
	chat = update.effective_chat
	checkstate(chat)
	context.bot.send_message(chat_id=chat.id,
							 text=f'Modo Spotify')
	users[chat.id].mode = 'spotify'
	

def link_d(update, context):
	print("prin")

	chat = update.effective_chat
	checkstate(chat)
	sons = nuevabusqueda(update.message.text, playlist=True)
	songs = nuevadescarga(sons, playlist=True)
	print(songs)
#context.bot.send_message(chat_id=chat.id,
							# text=f'Descargando')
	#users[chat.id].download(context)

def youtubemode(update, context):
	chat = update.effective_chat
	checkstate(chat)
	context.bot.send_message(chat_id=chat.id,
							 text=f'Modo youtube')
	users[chat.id].mode = "youtube"

def recomendacion(update, context):
	chat = update.effective_chat
	checkstate(chat)
	print(users[chat.id].genres, users[chat.id].songhistory)
	if len(users[chat.id].songhistory) >= 2:
		songhref = getrecomendaciones(
			users[chat.id].songhistory[:-2],
			users[chat.id].genres[:-1],
			'',
		)
		song, path = nuevadescarga(songhref)
		context.bot.send_audio(chat_id=chat.id, audio=open(path, 'rb'))
		os.remove(path)
	else :
		context.bot.send_message(chat_id=chat.id,
							 text='Necesitas mas canciones')


# async def inline_mode(update, context):
# 	query = update.inline_query.query
# 	results=[InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="Caps")]
	
	# input_message_content=InputTextMessageContent(query.upper()),
def album(update, context):
	chat = update.effective_chat
	checkstate(chat)
	#global songs
	st = update.message.text.replace("/album ","")
	print(st)

	
	sons = nuevabusqueda(st, playlist=True)
	songs = nuevadescarga(sons, playlist=True)
	for song in songs:
		context.bot.send_audio(chat_id=chat.id, audio=open(song[1], 'rb'))
		print(song[1])
		os.remove(song[1])
		#os.remove(song.path)
	#print(songs)
	
#
	#users[chat.id].download(context)

def audio_handler(update, context) -> None:
	chat = update.effective_chat
	checkstate(chat)
	context.bot.send_message(chat_id=chat.id,
                             text="Buscando")
	file = context.bot.getFile(update.message.voice)
	song = detectsong(file.file_path)
	if song == "nope":
		context.bot.send_message(chat_id=chat.id,
                             text="No se encontro la cancion")
	else:
		users[chat.id].title = str(song['name'] + ' ' + song['artist'])
		users[chat.id].son = nuevabusqueda(users[chat.id].title)
		message = f" {song['name']} {song['artist']} \n album: {song['album']} \n {song['url']} \n "
		# message = escape(message, "\\", x)
		button = [[InlineKeyboardButton("Descargar", callback_data="descargar-spotify-audio")]]
		context.bot.send_photo(photo=song['image'], chat_id=update.effective_chat.id,
	                             caption=message, reply_markup=InlineKeyboardMarkup(button))
		#context.bot.send_photo()
		print(file)
		# print ("file_id: " + str(update.message.voice.file_id))
		# file.download('voice.ogg')

def queryhandler(update, context):
	query = update.callback_query.data
	chat = update.effective_chat
	checkstate(chat)
	if "descargar-spotify-audio" in query:
		descargar(update, context, chat.id, "spotify"	)
	if "descargar-youtube-audio" in query:
		descargar(update, context, chat.id, "youtube"	)
	if "descargar-youtube-video" in query:
		descargar(update, context, chat.id, "youtube", "video"	)

def radio(update, context): 
  ##context.bot.send_audio(chat_id=update.effective_chat.id, title="Radio Uninorte"
	#$				 ,  performer="Universidad Del Norte", mime="audio/mpeg",
	#			   audio="http://radio-proxy.app.softworks.studio/stream.mp3")
			context.bot.send_message(
        chat_id=update.effective_chat.id, text="Unde el boton de abajo para abrir la radio de la Universidad Del Norte",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Abre La Radio De La Universidad Del Norte ",
                web_app=WebAppInfo(url="https://harmonious-crostata-0d8ebb.netlify.app"),
            )
        ),
    )

def quitradiobutton(update, context):
	context.bot.send_message(
        chat_id=update.effective_chat.id, text="Quitado",
				reply_markup=ReplyKeyboardRemove())



def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="No entiendo ese comando")


def main() -> None:
	updater = Updater(os.environ['BOTTOKEN'], use_context=True)
	
	dispatcher = updater.dispatcher

	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)
	
	echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
	dispatcher.add_handler(echo_handler)
	
	descargar_handler = CommandHandler('descargar', descargar)
	dispatcher.add_handler(descargar_handler)
	
	spotify = CommandHandler(['spotify', 'calidad'], spotifymode)
	dispatcher.add_handler(spotify)
	
	youtubeh = CommandHandler('youtube', youtubemode)
	dispatcher.add_handler(youtubeh)
	
	#dispatcher.add_handler(MessageHandler(Filters.entity('url'), album))

	dispatcher.add_handler(MessageHandler(Filters.voice & ~Filters.command, audio_handler))

	dispatcher.add_handler(CallbackQueryHandler(queryhandler))
	# application.add_handler(InlineQueryHandler(inline_query))
	dispatcher.add_handler(CommandHandler('recomiendame', recomendacion))
	
	dispatcher.add_handler(CommandHandler('radio', radio))
	dispatcher.add_handler(CommandHandler('album', album))
	dispatcher.add_handler(CommandHandler('quitar', quitradiobutton))
	
	dispatcher.add_handler(MessageHandler(Filters.command, unknown))
	
	updater.start_polling()


if __name__ == "__main__":
    main()
