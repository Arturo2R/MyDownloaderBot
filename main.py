from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InputMediaAudio
import logging
import os
from API import buscar, descarga
print(os.getenv("REPLIT_DB_URL"))

updater = Updater('1637478750:AAE8UnbLz6iQAfGvD2Oc3J2rFK5xYm2b0uc',
                  use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Soy un robot creado por arturoR, estoy aqui para facilitarte los domiciolios')

def echo(update, context):
      global song_title, song_url
      song_title, song_url = buscar(update.message.text)
      context.bot.send_message(chat_id=update.effective_chat.id,
                              text=f'te refieres a {song_title} {song_url}')
      context.bot.send_message(chat_id=update.effective_chat.id, text='Escribe el comando /descargar para descargar la cancion en mp3')
    
def descargar(update, context):
  context.bot.send_message(chat_id=update.effective_chat.id, text=f'Descargando {song_title}')
  file, file_title, file_author = descarga(song_url)
  print(file, file_title)
  
  context.bot.send_audio(chat_id=update.effective_chat.id, performer=file_author, audio=open(file, 'rb'))
  os.remove(file)
  

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
start_handler = CommandHandler('start', start)
link_handler = MessageHandler(Filters.entity('url'),descargar)
descargar_handler = CommandHandler('descargar', descargar)
dispatcher.add_handler(descargar_handler)
dispatcher.add_handler(link_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="No entiendo ese comando")


unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()