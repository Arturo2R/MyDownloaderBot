from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InputMediaAudio
import logging
import os


from API import buscar, descarga


regex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

class UserData:
	def __init__(self, chatid, songurl, search, title, username, first, last):
		self.chatid = chatid
		self.songurl = songurl
		self.search = search
		self.title = title
		self.username = username
		self.name = first + ' ' + last

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
		users[chat.id] = UserData(chat.id, '', '', '', chat.username, chat.first_name, chat.last_name)
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
	
	# global song_title, song_url
	song_title, song_url = buscar(update.message.text)
	users[chat.id].songurl = song_url
	users[chat.id].title = song_title

	context.bot.send_message(chat_id=chat.id, text=f'te refieres a {song_title} {song_url}')
	context.bot.send_message(
		chat_id=chat.id,
		text='Escribe el comando /descargar para descargar la cancion en webm')


def descargar(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	context.bot.send_message(chat_id=chat.id,
							 text=f'Descargando {users[chat.id].title}')
	users[chat.id].download(context)

def link_d(update, context):
	chat = update.effective_chat
	checkstate(chat)
	
	context.bot.send_message(chat_id=chat.id,
							 text=f'Descargando')
	users[chat.id].download(context)



def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="No entiendo ese comando")


def main() -> None:
    updater = Updater(os.environ['BOT-TOKEN'], use_context=True)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    descargar_handler = CommandHandler('descargar', descargar)
    dispatcher.add_handler(descargar_handler)

    link_handler = MessageHandler(Filters.entity('url'), link_d)
    dispatcher.add_handler(link_handler)

    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()


if __name__ == "__main__":
    main()
