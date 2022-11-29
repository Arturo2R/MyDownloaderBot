import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from telegram import InputMediaAudio, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup, constants
from API import buscar, descarga, nuevadescarga, getrecomendaciones, detectsong

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

class UserData:
	def __init__(self, chatid, songurl, search, title, username, first, last, mode, songhistory, artisthistory, genres):
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
		

	def __str__(self):
		return f"user:{self.name} id:{self.chatid} url:{self.songurl} query:{self.search}"

	def download(self, context):
		file, file_title, file_author = descarga(self.songurl)
		print(file, file_title)
		context.bot.send_audio(chat_id=self.chatid,
						   performer=file_author,
						   audio=open(file, 'rb'))
		os.remove(file)



users = {
  "prop": "todo"
}

def checkstate(chat):
	if chat.id in users: 
		print('all okey')
	else:
		users[chat.id] = UserData(chat.id, '', '', '', chat.username, chat.first_name, chat.last_name, 'spotify', [], [], [])
	print(users[chat.id])
	

def start(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	context.bot.send_message(
        chat_id=chat.id,
        text=
        f'Hola {chat.first_name} Soy un robot creado por arturoR, estoy aqui para descargar musica por ti'
    )


def echo(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	if users[chat.id].mode == 'youtube': 
		# global song_title, song_url
		song_title, song_url = buscar(update.message.text)
		users[chat.id].songurl = song_url
		users[chat.id].title = song_title
	
		context.bot.send_message(chat_id=chat.id, text=f'te refieres a {song_title} {song_url}')
		context.bot.send_message(
			chat_id=chat.id,
			text='Escribe el comando /descargar para descargar la cancion en webm')
	if users[chat.id].mode == 'spotify':
		context.bot.send_message(chat_id=chat.id,
							 text=f'Descargando')
		# print(context)
		print(update.message.text)
		song, path = nuevadescarga(update.message.text.replace("/spotify", " "))
		context.bot.send_audio(chat_id=chat.id, audio=open(path, 'rb'))
		
		if song.song_id not in users[chat.id].songhistory :
			users[chat.id].songhistory.append(song.song_id)

		users[chat.id].genres.extend(song.genres)
		
		os.remove(path)
		

def descargar(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	context.bot.send_message(chat_id=chat.id,
							 text=f'Descargando {users[chat.id].title}')
	users[chat.id].download(context)

def spotifymode(update, context):
	print("spot")
	chat = update.effective_chat
	checkstate(chat)
	context.bot.send_message(chat_id=chat.id,
							 text=f'Modo Spotify')
	users[chat.id].mode = 'spotify'
	

def link_d(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	context.bot.send_message(chat_id=chat.id,
							 text=f'Descargando')
	users[chat.id].download(context)

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
							 text=f'Necesitas mas canciones')

# async def inline_mode(update, context):
# 	query = update.inline_query.query
# 	results=[InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="Caps")]
	
	# input_message_content=InputTextMessageContent(query.upper()),

x = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
escape = lambda s, escapechar, specialchars: "".join(escapechar + c if c in specialchars or c == escapechar else c for c in s)

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
		message = f" {song['name']} {song['artist']} \n album: {song['album']} \n {song['url']} \n "
		message = escape(message, "\\", x)
		button = [[InlineKeyboardButton("Descargar", callback_data="descargar")]]
		context.bot.send_message(chat_id=update.effective_chat.id,
	                             text=message, parse_mode=constants.PARSEMODE_MARKDOWN_V2, reply_markup=InlineKeyboardMarkup(button))
		
		print(file)
		# print ("file_id: " + str(update.message.voice.file_id))
		# file.download('voice.ogg')

def queryhandler(update, context):
	query = update.callback_query.data
	chat = update.effective_chat
	checkstate(chat)
	if "descargar" in query:
		context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Descargando") 
		song, path = nuevadescarga(users[chat.id].title)	
		context.bot.send_audio(chat_id=chat.id, audio=open(path, 'rb'))
		if song.song_id not in users[chat.id].songhistory :
			users[chat.id].songhistory.append(song.song_id)

		users[chat.id].genres.extend(song.genres)
		
		os.remove(path)


def audio_handler(update, context) -> None:
	chat = update.effective_chat
	checkstate(chat)
	context.bot.send_message(chat_id=chat.id,
                             text="Buscando")
	file = context.bot.getFile(update.message.voice)
	song = detectsong(file.file_path)
	users[chat.id].title = song['name'] + ' - ' + song['artist']
	message = f" *{song['name']}* \- _{song['artist']}_ \n album: {song['album']} \n {song['url']} \n "
	button = [[InlineKeyboardButton("Descargar", callback_data="descargar")]]
	context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message, parse_mode=constants.PARSEMODE_MARKDOWN_V2, reply_markup=InlineKeyboardMarkup(button))
	
	print(file)
	# print ("file_id: " + str(update.message.voice.file_id))
	# file.download('voice.ogg')

def queryhandler(update, context):
	query = update.callback_query.data
	chat = update.effective_chat
	checkstate(chat)
	
	if "descargar" in query:
		song, path = nuevadescarga(users[chat.id].title)	
		context.bot.send_audio(chat_id=chat.id, audio=open(path, 'rb'))
		if song.song_id not in users[chat.id].songhistory :
			users[chat.id].songhistory.append(song.song_id)

		users[chat.id].genres.extend(song.genres)
		
		os.remove(path)



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
	
	link_handler = MessageHandler(Filters.entity('url'), link_d)

	dispatcher.add_handler(MessageHandler(Filters.voice & ~Filters.command, audio_handler))
	dispatcher.add_handler(CallbackQueryHandler(queryhandler))

	# application.add_handler(InlineQueryHandler(inline_query))
	dispatcher.add_handler(CommandHandler('recomiendame', recomendacion))
	dispatcher.add_handler(link_handler)
	
	dispatcher.add_handler(MessageHandler(Filters.command, unknown))
	
	updater.start_polling()


if __name__ == "__main__":
    main()
