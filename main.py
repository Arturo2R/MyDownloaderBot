import logging
import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

import nest_asyncio
import math
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    constants,
)
from API import (
    buscar,
    descargayoutube,
    nuevadescarga,
    getrecomendaciones,
    detectsong,
    nuevabusqueda,
    search_album,
)


nest_asyncio.apply()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class UserData:
    def __init__(
        self,
        update,
        context,
        chatid,
        songurl,
        search,
        title,
        username,
        first,
        last,
        mode,
        songhistory,
        artisthistory,
        genres,
        song,
        album,
    ):
        self.update = update
        self.context = context
        self.id = chatid
        self.songurl = songurl
        self.search = search
        self.title = title
        self.username = username
        self.name = first
        self.mode = mode
        self.songhistory = songhistory
        self.artishistory = artisthistory
        self.genres = genres
        self.song = song
        self.album = album

    def __str__(self):
        return f"user:{self.name} id:{self.id} url:{self.songurl} query:{self.search}"

    async def download(self, type: "audio" or "video" = "audio"):
        tipo = type
        await self.context.bot.send_message(chat_id=self.id, text="Descargando")
        if self.mode == "spotify":
            song, path = nuevadescarga(self.song)
            if song.song_id not in self.songhistory:
                self.songhistory.append(song.song_id)
            self.genres.extend(song.genres)
        elif self.mode == "youtube":
            path = descargayoutube(self.songurl, tipo)

        await self.context.bot.send_audio(chat_id=id, audio=open(path, "rb"))
        os.remove(path)

    async def changeMode(self, modes: "spotify" or "youtube"):
        if modes == "spotify":
            strin = "Spotify"
        else:
            strin = "Youtube"
        await self.context.bot.send_message(chat_id=self.id, text=f"Modo {strin}")
        self.mode = modes

    async def searchSong(self):
        if self.mode == "youtube":
            # global song_title, song_url
            song_title, song_url = buscar(self.update.message.text)
            self.songurl = song_url
            self.title = song_title
            await self.showCard()

        if self.mode == "spotify":
            # print(context)
            song = nuevabusqueda(self.update.message.text)
            self.songurl = song.url
            self.title = song.name
            self.song = song
            self.album = song.album_name
            await self.showCard()

        if self.mode == "album":
            await album(self.update, self.context)

    async def showCard(self):
        # artist=escape(artist, "\\", x)
        # name=escape(name, "\\", x)
        # image=escape(image, "\\", x)
        # album=escape(album, "\\", x)
        # source=escape(source, "\\", x)
        if self.mode == "spotify":
            if self.song.album_artist == "nope":
                message = f"Te refieres a {album.name} \n {self.album.url} \n "
            else:
                message = f" {self.song.display_name} \nalbum: {self.song.album_name} \n{self.song.url} \n "
                self.title = self.song.display_name
        elif self.mode == "youtube":
            message = f"Te refieres a {self.title} \n {self.songurl} \n "
        # message = escape(message, "/", x)
        button = [
            [
                InlineKeyboardButton(
                    "Descargar", callback_data=f"descargar-{self.mode}-audio"
                )
            ]
        ]
        # if source == "youtube":
        # button.append([InlineKeyboardButton("Descargar Video", callback_data=f"descargar-{source}-video")])
        await self.context.bot.send_message(
            chat_id=self.id, text=message, reply_markup=InlineKeyboardMarkup(button)
        )


users: {int: UserData, int: UserData} = {
    121212: "FSFSD",
}


def checkstate(update, context, chat):
    if chat.id in users:
        users[chat.id].update = update
        users[chat.id].context = context
        print("all okey")
    else:
        users[chat.id] = UserData(
            update,
            context,
            chat.id,
            "",
            "",
            "",
            chat.username,
            chat.first_name,
            " ",
            "spotify",
            [],
            [],
            [],
            "",
            "",
        )
    print(users[chat.id])


x = [
    "-",
    ".",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    "!",
]
escape = lambda s, escapechar, specialchars: "".join(
    escapechar + c if c in specialchars or c == escapechar else c for c in s
)


async def mostrartarjeta(
    update,
    context,
    user: UserData,
    name: str,
    source: "spotify" or "youtube",
    url: str,
    artist="nope",
    image="nope",
    album="nope",
):
    # artist=escape(artist, "\\", x)
    # name=escape(name, "\\", x)
    # image=escape(image, "\\", x)
    # album=escape(album, "\\", x)
    # source=escape(source, "\\", x)
    if artist == "nope":
        message = f"Te refieres a {name} \n {url} \n "
    else:
        message = f" {name} {artist} \n album: {album} \n {url} \n "
        user.title = str(name + " " + artist)
    # message = escape(message, "\\", x)
    button = [
        [InlineKeyboardButton("Descargar", callback_data=f"descargar-{source}-audio")]
    ]
    # if source == "youtube":
    # button.append([InlineKeyboardButton("Descargar Video", callback_data=f"descargar-{source}-video")])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=InlineKeyboardMarkup(button),
    )


async def descargar(update, context, id, source, type: "audio" or "video" = "audio"):
    tipo = type
    await context.bot.send_message(chat_id=id, text="Descargando")
    if source == "spotify":
        song, path = nuevadescarga(users[id].song)
        if song.song_id not in users[id].songhistory:
            users[id].songhistory.append(song.song_id)
        users[id].genres.extend(song.genres)
    elif source == "youtube":
        path = descargayoutube(users[id].songurl, tipo)

    await context.bot.send_audio(chat_id=id, audio=open(path, "rb"))
    os.remove(path)


async def start(update, context):
    chat = update.effective_chat
    checkstate(update, context, chat)

    await context.bot.send_message(
        chat_id=chat.id,
        text=f"Hola {chat.first_name} Soy un robot creado por @arturo2r, estoy aqui para descargar musica por ti",
    )


async def echo(update, context):
    chat = update.effective_chat
    checkstate(update, context, chat)
    await users[chat.id].searchSong()


# async def descargar(update, context):
# 	chat = update.effective_chat
# 	checkstate(update, context, chat)

# 	await context.bot.send_message(chat_id=chat.id,
# 							 text=f'Descargando {users[chat.id].title}')
# 	users[chat.id].download(context)


async def spotifymode(update, context):
    print("spot")
    chat = update.effective_chat
    checkstate(update, context, chat)
    await users[chat.id].changeMode("spotify")

    if "https://" in update.message.text:
        await users[chat.id].searchSong()


async def link_d(update, context):
    print("prin")

    chat = update.effective_chat
    checkstate(update, context, chat)
    sons = nuevabusqueda(update.message.text, playlist=True)
    songs = await nuevadescarga(sons, playlist=True)
    print(songs)


# await context.bot.send_message(chat_id=chat.id,
# text=f'Descargando')
# users[chat.id].download(context)


async def youtubemode(update, context):
    print("youtubeMode")
    chat = update.effective_chat
    checkstate(update, context, chat)
    await users[chat.id].changeMode("youtube")

    if "https://" in update.message.text:
        await users[chat.id].searchSong()


async def recomendacion(update, context):
    chat = update.effective_chat
    checkstate(update, context, chat)
    print(users[chat.id].genres, users[chat.id].songhistory)
    if len(users[chat.id].songhistory) >= 2:
        songhref = getrecomendaciones(
            users[chat.id].songhistory[:-2],
            users[chat.id].genres[:-1],
            "",
        )
        song, path = await nuevadescarga(songhref)
        await context.bot.send_audio(chat_id=chat.id, audio=open(path, "rb"))
        os.remove(path)
    else:
        await context.bot.send_message(chat_id=chat.id, text="Necesitas mas canciones")


# async async def inline_mode(update, context):
# 	query = update.inline_query.query
# 	results=[InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="Caps")]

# input_message_content=InputTextMessageContent(query.upper()),


# async def send_songs(context, id, songs):
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = [executor.submit(asyncio.run, send_song(context, id, song)) for song in songs]
#         for future in concurrent.futures.as_completed(futures):
#             try:
#                 result = future.result()
#             except Exception as e:
#                 print(f"An error occurred: {e}")
#                 await context.bot.send_message(chat_id=id, text=f"An error occurred: {e}")

# async def send_song(context, id, song):
# 	try:
# 		await context.bot.send_audio(chat_id=id, audio=open(song[1], 'rb'))
# 		print(song[1])
# 		# os.remove(song[1])
# 	except:
# 		await context.bot.send_message(chat_id=id,
# 							text=f'No se pudo enviar una a cancion')
# 	print(f"Sending {song[0]} to the user...")


async def album(update, context) -> None:
    chat = update.effective_chat
    checkstate(update, context, chat)
    await context.bot.send_message(chat_id=chat.id, text=f"Buscando Playlist")
    # global songs
    if (update.message.text == "/album") or (
        update.message.text == "/album@downloaderbot"
    ):
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"Modo Busqueda De Album \nEscribe el nombre del album que quieres buscar",
        )
        users[chat.id].mode = "album"
        return

    st = update.message.text.replace("/album ", "")
    if not "https" in st:
        st = search_album(st)
    print(st)
    sons = nuevabusqueda(st, playlist=True)
    playListName = escape(sons[0].list_name, "\\", x)
    message = f"*Canciones de {playListName}* \n"
    message = escape(message, "\\", x)
    songNames = []
    totalSongSeconds = 0
    await context.bot.send_photo(
        chat_id=chat.id,
        caption=f"Album: {playListName}",
        photo=sons[0].cover_url,
    )
    # Haciendo el string del mensaje y mandandolo
    ## Cuantos mensajes hay que mandar, se manda un mensaje por cada 50 canciones
    messageQuantity: int = math.ceil(sons.__len__() / 50)
    sons.sort(key=lambda x: x.list_position)
    for song in sons:
        songNames.append(
            f"    {str(song.list_position)} *{song.name}* de _{song.artist}_ {'y ' + song.artists[1] if len(song.artists) > 1 else ''} \n"
        )
        totalSongSeconds = totalSongSeconds + song.duration
    for i in range(messageQuantity):
        songListNames = message + escape(
            "".join(songNames[i * 50 : i * 50 + 50]), "\\", x
        )
        await context.bot.send_message(
            chat_id=chat.id, text=songListNames, parse_mode="MarkdownV2"
        )

    # ## Mensaje de Cuanto contenido sera
    # await context.bot.send_message(
    #     chat_id=chat.id,
    #     text=f"Son {str(math.floor(totalSongSeconds/1000/60))} minutos de canciones",
    #     parse_mode="MarkdownV2",
    # )

    ## Mensaje de Cuanto tiempo se demorara en descargarse
    button = [[InlineKeyboardButton("Descargar", callback_data=f"descargar-album")]]
    await context.bot.send_message(
        chat_id=chat.id,
        text=f"Se demorara {str(math.floor(totalSongSeconds/1000/60*0.1))} minutos en descargarse",
        reply_markup=InlineKeyboardMarkup(button),
        parse_mode="MarkdownV2",
    )
    users[chat.id].album = sons

    # await send_songs(context, chat.id, songs)

    # print(songs)


async def descarga_album(update, context):
    chat = update.effective_chat
    sons = users[chat.id].album
    await context.bot.send_message(
        chat_id=chat.id, text=f"Descargando {sons.__len__()} canciones"
    )
    songs = nuevadescarga(sons, playlist=True)
    # print(sons)
    no_downloaded: int = 0
    for song in songs:
        try:
            await context.bot.send_audio(chat_id=chat.id, audio=open(song[1], "rb"))
            print(song[1])
            os.remove(song[1])
        except:
            no_downloaded = no_downloaded + 1
            await context.bot.send_message(
                chat_id=chat.id, text=f"No se pudo enviar una a cancion"
            )

    await context.bot.send_message(
        chat_id=chat.id, text=f"✅ {sons.__len__()-no_downloaded} canciones descargadas"
    )


#
# users[chat.id].download(context)


## Move to utils
async def download_audio(audio) -> str:
    # download the file and rename it to end with ogg extension and save it in the same path of the script and save the path
    path = await audio.download_to_drive()
    filename, extension = os.path.splitext(path)

    # change the extension to '.ogg'
    new_path = filename + ".ogg"
    # rename the file
    os.rename(path, new_path)
    return new_path


async def audio_handler(update, context) -> None:
    chat = update.effective_chat
    checkstate(update, context, chat)

    await context.bot.send_message(chat_id=chat.id, text="Buscando")

    file = await context.bot.getFile(update.message.voice)
    path = await download_audio(file)
    song = detectsong(path)

    if song == "nope":
        await context.bot.send_message(
            chat_id=chat.id, text="No se encontro la cancion"
        )

    else:
        users[chat.id].title = str(song["name"] + " " + song["artist"])
        users[chat.id].song = nuevabusqueda(users[chat.id].title)
        message = f" {song['name']} {song['artist']} \n album: {song['album']} \n {song['url']} \n "
        # message = escape(message, "\\", x)
        button = [
            [InlineKeyboardButton("Descargar", callback_data="descargar-spotify-audio")]
        ]
        await context.bot.send_photo(
            photo=song["image"],
            chat_id=update.effective_chat.id,
            caption=message,
            reply_markup=InlineKeyboardMarkup(button),
        )
        os.remove(path)
        # await context.bot.send_photo()

        # print ("file_id: " + str(update.message.voice.file_id))
        # file.download('voice.ogg')


async def queryhandler(update, context):
    query = update.callback_query.data
    chat = update.effective_chat
    checkstate(update, context, chat)
    if "descargar-spotify-audio" in query:
        await descargar(update, context, chat.id, "spotify", "audio")
    elif "descargar-youtube-audio" in query:
        await descargar(update, context, chat.id, "youtube", "audio")
    elif "descargar-youtube-video" in query:
        await descargar(update, context, chat.id, "youtube", "video")
    elif "descargar-album" in query:
        await descarga_album(update, context)


async def radio(update, context):
    ##await context.bot.send_audio(chat_id=update.effective_chat.id, title="Radio Uninorte"
    # $				 ,  performer="Universidad Del Norte", mime="audio/mpeg",
    # 			   audio="http://radio-proxy.app.softworks.studio/stream.mp3")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Unde el boton de abajo para abrir la radio de la Universidad Del Norte",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Abre La Radio De La Universidad Del Norte ",
                web_app=WebAppInfo(
                    url="https://harmonious-crostata-0d8ebb.netlify.app"
                ),
            )
        ),
    )


async def quitradiobutton(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Quitado",
        reply_markup=ReplyKeyboardRemove(),
    )


async def unknown(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="No entiendo ese comando"
    )


def main() -> None:
    app = Application.builder().token(os.environ["BOTTOKEN"]).read_timeout(60).build()

    start_handler = CommandHandler("start", start)
    app.add_handler(start_handler)

    spotify_link_handler = MessageHandler(
        filters.Regex(
            r"https:\/\/open\.spotify\.com(\/intl-es)?\/(album|playlist)\/[A-Za-z0-9?=_-]+"
        ),
        album,
    )
    app.add_handler(spotify_link_handler)

    spotify_link_handler = MessageHandler(
        filters.Regex(
            r"https:\/\/open\.spotify\.com(\/intl-es)?\/track\/[A-Za-z0-9?=_-]+"
        ),
        spotifymode,
    )
    app.add_handler(spotify_link_handler)

    youtube_link_handler = MessageHandler(
        filters.TEXT
        & filters.Regex(
            r"(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11})"
        ),
        youtubemode,
    )
    app.add_handler(youtube_link_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    app.add_handler(echo_handler)

    descargar_handler = CommandHandler("descargar", descargar)
    app.add_handler(descargar_handler)

    spotify = CommandHandler(["spotify", "calidad"], spotifymode)
    app.add_handler(spotify)

    youtubeh = CommandHandler("youtube", youtubemode)
    app.add_handler(youtubeh)

    # app.add_handler(MessageHandler(Filters.entity('url'), album))

    app.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, audio_handler))

    app.add_handler(CallbackQueryHandler(queryhandler))
    # application.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CommandHandler("recomiendame", recomendacion))

    app.add_handler(CommandHandler("radio", radio))
    app.add_handler(CommandHandler("album", album))
    app.add_handler(CommandHandler("quitar", quitradiobutton))

    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Se ejecuta la clase y el constructor creara un objeto que se guardará en app

    # app.run_polling(stop_signals=None)

    app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        secret_token="ASecretTokenIHaveChangedByNoww",
        webhook_url="https://9567-191-88-98-128.ngrok-free.app",
        # webhook_url="https://e805-191-88-98-128.ngrok-free.app",
    )


if __name__ == "__main__":
    main()
