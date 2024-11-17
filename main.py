import asyncio
import json
import logging
import math
import os
from typing import Dict

import nest_asyncio
from openai import OpenAI
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from API import (
    detectsong,
    download_spotify,
    download_youtube,
    recomendation,
    search_album,
    search_spotify,
    search_youtube,
)

# from icecream import ic

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.environ.get("OPENAI_API_KEY"),
)

nest_asyncio.apply()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class UserData:
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        id,
        username: str,
        first_name: str,
        thread,
        songurl: str = None,
        search=None,
        title=None,
        last=None,
        mode="spotify",
        songhistory=None,
        artisthistory=None,
        genres=None,
        song=None,
        album=None,
    ):
        self.update = update
        self.context = context
        self.id = id
        self.songurl = songurl
        self.search = search
        self.title = title
        self.username = username
        self.name = first_name
        self.mode = mode
        self.songhistory = songhistory if songhistory is not None else []
        self.artishistory = artisthistory
        self.genres = genres
        self.song = song
        self.album = album
        self.thread = thread

    def __str__(self):
        return f"user:{self.name} id:{self.id} "

    async def sendSong(self, song):
        print(f"Sending {song} song to {self.username}")
        await self.context.bot.send_audio(chat_id=self.id, audio=open(song, "rb"))
        os.remove(song)

    async def sendMessage(self, message: str, **otherParams):
        print(f"Sending {message} song to  {self.username}")

        await self.context.bot.send_message(
            chat_id=self.id, text=message, **otherParams
        )

    async def sendPhoto(self, photo, caption: str, **otherParams):
        print(f"Sending photo to {self.username}")

        await self.context.bot.send_photo(
            chat_id=self.id, caption=caption, photo=photo, **otherParams
        )

    async def download(self, typ: str = None, url=None):
        print(f"Downloading {typ} song for {self.username}")

        await self.sendMessage("Descargando")
        mode = typ or self.mode

        if mode == "spotify":
            if url:
                # THis changes the self.song y self.songurl to the url of the song
                self.searchSong(query=url, mode="spotify")
            song, path = download_spotify(self.song)

            if song.song_id and song.song_id not in self.songhistory:
                self.songhistory.append(song.song_id)
            if song.genres:
                self.genres.extend(song.genres)

        elif mode == "youtube":
            path = download_youtube(url or self.songurl, "audio")

        await self.sendSong(path)

    async def changeMode(self, modes):
        if modes == "spotify":
            strin = "Spotify"
        elif modes == "album":
            strin = "Album"
        else:
            strin = "Youtube"
        await self.sendMessage(f"Modo {strin}")
        self.mode = modes

    async def searchSong(self, query=None, mode=None):
        searchQuery = query or self.update.message.text
        mode = mode or self.mode
        if mode == "youtube":
            # global song_title, song_url
            song_title, song_url = search_youtube(searchQuery)
            self.songurl = song_url
            self.title = song_title
            await self.showCard(mode="youtube")

        if mode == "spotify":
            # print(context)
            song = search_spotify(searchQuery)
            self.songurl = song.url
            self.title = song.name
            self.song = song
            self.album = song.album_name
            await self.showCard(mode="spotify")
            return f"title: {self.title}, url: {self.songurl}"

        if mode == "album":
            await album(self.update, self.context)

        if mode == "ai":
            await AI(self.update, self.context)

    async def showCard(self, mode: str = None):
        mode = mode or self.mode
        if mode == "spotify":
            if self.song.album_artist == "nope":
                message = f"Te refieres a {self.album.name} \n {self.album.url} \n "
            else:
                message = f" {self.song.display_name} \nalbum: {self.song.album_name} \n{self.song.url} \n "
                self.title = self.song.display_name

        elif mode == "youtube":
            message = f"Te refieres a {self.title} \n {self.songurl} \n "

        button = [
            [
                InlineKeyboardButton(
                    "Descargar", callback_data=f"descargar-{self.mode}-audio"
                )
            ]
        ]

        await self.sendMessage(message, reply_markup=InlineKeyboardMarkup(button))


users: Dict[int, UserData] = {
    121212: "FSFSD",
}


def checkstate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> UserData:
    chat = update.effective_chat
    if chat.id in users:
        users[chat.id].update = update
        users[chat.id].context = context
        print("all okey")
    else:
        thread = (
            client.beta.threads.create()
        )  # Create a thread to use with the assistant and save it in the user object

        users[chat.id] = (
            UserData(  # Create a user object and save it in the users dictionary
                update=update,
                context=context,
                id=chat.id,
                username=chat.username,
                first_name=chat.first_name,
                mode="spotify",
                thread=thread,
            )
        )

    print(users[chat.id])
    return users[chat.id]


x = [  # Special characters to escape
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

def escape(s, escapechar, specialchars):
    return "".join(escapechar + c if c in specialchars or c == escapechar else c for c in s)


def es(message):
    return escape(message, "\\", x)


# async def mostrartarjeta(
#     update,
#     context,
#     user: UserData,
#     name: str,
#     source: "spotify" or "youtube",
#     url: str,
#     artist="nope",
#     image="nope",
#     album="nope",
# ):
#     # artist=escape(artist, "\\", x)
#     # name=escape(name, "\\", x)
#     # image=escape(image, "\\", x)
#     # album=escape(album, "\\", x)
#     # source=escape(source, "\\", x)
#     if artist == "nope":
#         message = f"Te refieres a {name} \n {url} \n "
#     else:
#         message = f" {name} {artist} \n album: {album} \n {url} \n "
#         user.title = str(name + " " + artist)
#     # message = escape(message, "\\", x)
#     button = [
#         [InlineKeyboardButton("Descargar", callback_data=f"descargar-{source}-audio")]
#     ]
#     # if source == "youtube":
#     # button.append([InlineKeyboardButton("Descargar Video", callback_data=f"descargar-{source}-video")])
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=message,
#         reply_markup=InlineKeyboardMarkup(button),
#     )


# async def descargar(update, context, id, source, type: "audio" or "video" = "audio"):
#     tipo = type
#     await context.bot.send_message(chat_id=id, text="Descargando")
#     if source == "spotify":
#         song, path = download_spotify(users[id].song)
#         if song.song_id not in users[id].songhistory:
#             users[id].songhistory.append(song.song_id)
#         users[id].genres.extend(song.genres)
#     elif source == "youtube":
#         path = download_youtube(users[id].songurl, tipo)

#     await context.bot.send_audio(chat_id=id, audio=open(path, "rb"))
#     os.remove(path)


async def help(update, context):
    user = checkstate(update, context)
    prompt = (
        "¿Que puedo hacer por ti?\n"
        "\n"
        "Si me envias un **mensaje de voz** grabando una cancion la analizare por ti, te dire el nombre y podras descargarla\n"
        "\n"
        "/start - Inicia el bot\n"
        "/help - Muestra este mensaje\n"
        "/youtube - Modo Spotify para buscar canciones usando spotify\n"
        "/spotify - COn este modo puedes buscar caciones usando Youtube\n"
        "/ai [Pregunta] - Con este comando puedes utilizar el nuestro asistente experto en musica\n"
        # "/play [nombre de la cancion] - Descarga la cancion y la envia\n"
        "/album [nombre de la playlist] - Descarga el album y la envia\n"
        "/searchplaylist [nombre de la playlist] - Muestra una lista de playlist para que elijas cual descargar\n"
        # "/playlist - Muestra la playlist que se esta reproduciendo\n"
        # "/ping - Muestra el tiempo de respuesta\n"
        "\n"
        # "Puedes usar /help [comando] para obtener ayuda sobre un comando especifico"
    )
    await user.sendMessage(es(prompt), parse_mode="MarkdownV2")


async def start(update, context):
    user = checkstate(update, context)

    await user.sendMessage(
        f"Hola {user.username} Soy un robot creado por @arturo2r, estoy aqui para descargar musica por ti"
    )


async def echo(update, context):
    user = checkstate(update, context)

    await user.searchSong()


async def spotifymode(update, context):
    print("spot")
    user = checkstate(update, context)
    await user.changeMode("spotify")  # Cambiar el modo a youtube


# async def link_d(update, context):
#     print("prin")

#     user = checkstate(update, context)
#     sons = search_spotify(update.message.text, playlist=True)
#     songs = await download_spotify(sons, playlist=True)
#     print(songs)


async def youtubemode(update, context):
    print("youtubeMode")
    user = checkstate(update, context)

    # if update.message.text.replace("/youtube ", "") != "":
    #     await users[chat.id].searchSong()
    # elif "https://" in update.message.text:
    #     await users[chat.id].searchSong()
    await user.changeMode("youtube")  # Cambiar el modo a youtube


async def recomendacion(update, context):
    user = checkstate(update, context)
    print(user.genres, user.songhistory)
    if len(user.songhistory) >= 2:
        songhref = recomendation(
            user.songhistory[:-2],
            user.genres[:-1],
            "",
        )
        song, path = await download_spotify(songhref)
        await user.sendSong(path)
    else:
        await user.sendMessage("Necesitas mas canciones")


# async async def inline_mode(update, context):
# 	query = update.inline_query.query
# 	results=[InlineQueryResultArticle(
#             id=str(uuid4()),
#             title="Caps")]


# input_message_content=InputTextMessageContent(query.upper()),
async def album(update, context) -> None:
    user = checkstate(update, context)
    await user.sendMessage("Buscando Playlist")
    # global songs
    if (update.message.text == "/album") or (
        update.message.text == "/album@downloaderbot"
    ):
        await user.sendMessage(
            "Modo Busqueda De Album \nEscribe el nombre del album que quieres buscar"
        )

        user.mode = "album"
        return

    st = update.message.text.replace("/album ", "")
    if "https" not in st:
        # Search for the album
        try:
            st = search_album(st)
        except Exception:
            await user.sendMessage("No se encontró el álbum")
            return
    sons = search_spotify(st, playlist=True)
    playListName: str = escape(sons[0].list_name, "\\", x)
    message: str = f"*Canciones de [{es(playListName)}]({sons[0].list_url})* \n"
    songNames: list[str] = []
    totalSongSeconds: int = 0
    await user.sendPhoto(
        photo=sons[0].cover_url,
        caption=f"Album: {playListName}",
    )

    # Haciendo el string del mensaje y mandandolo
    ## Cuantos mensajes hay que mandar, se manda un mensaje por cada 50 canciones
    messageQuantity: int = math.ceil(sons.__len__() / 50)

    sons.sort(key=lambda x: x.list_position)

    for song in sons:
        totalSongSeconds = totalSongSeconds + song.duration
        songNames.append(
            f"    {str(song.list_position)}\. *[{es(song.name)}]({song.url})* de _{es(song.artist)}_ {'y ' + es(song.artists[1]) if len(song.artists) > 1 else ''} \n"
        )

    for i in range(messageQuantity):
        songListNames = message + "".join(songNames[i * 50 : i * 50 + 50])

        await user.sendMessage(
            songListNames,
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )

    # ## Mensaje de Cuanto contenido sera - No Borrar
    # await context.bot.send_message(
    #     chat_id=chat.id,
    #     text=f"Son {str(math.floor(totalSongSeconds/1000/60))} minutos de canciones",
    #     parse_mode="MarkdownV2",
    # )

    ## Mensaje de Cuanto tiempo se demorara en descargarse
    button = [[InlineKeyboardButton("Descargar", callback_data="descargar-album")]]
    demora = str(math.floor(((totalSongSeconds / 1000) / 60) * 0.1))
    await user.sendMessage(
        f"Se demorara {demora} minutos en descargarse",
        reply_markup=InlineKeyboardMarkup(button),
        parse_mode="MarkdownV2",
    )

    user.album = sons


async def descarga_album(update, context):
    user = checkstate(update, context)
    sons = user.album

    await user.sendMessage(f"Descargando {sons.__len__()} canciones")

    songs = download_spotify(sons, playlist=True)
    # print(sons)
    no_downloaded: int = 0
    for song in songs:
        try:
            await user.sendSong(song[1])

        except Exception:
            no_downloaded = no_downloaded + 1
            await user.sendMessage("No se pudo enviar una a cancion")

    await user.sendMessage(f"✅ {sons.__len__()-no_downloaded} canciones descargadas")


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
    user = checkstate(update, context)

    await user.sendMessage("Buscando")

    file = await context.bot.getFile(update.message.voice)
    path = await download_audio(file)
    song = detectsong(path)

    if song == "nope":
        await user.sendMessage("No se encontro la cancion")

    else:
        user.title = str(song["name"] + " " + song["artist"])
        user.song = search_spotify(user.title)
        message = f" {song['name']} {song['artist']} \n album: {song['album']} \n {song['url']} \n "
        # message = escape(message, "\\", x)
        button = [
            [InlineKeyboardButton("Descargar", callback_data="descargar-spotify-audio")]
        ]
        await user.sendPhoto(
            photo=song["image"],
            caption=message,
            reply_markup=InlineKeyboardMarkup(button),
        )
        os.remove(path)
        # await context.bot.send_photo()

        # print ("file_id: " + str(update.message.voice.file_id))
        # file.download('voice.ogg')


async def queryhandler(update, context):
    query = update.callback_query.data
    user = checkstate(update, context)
    if user is None:
        return

    if "descargar-spotify-audio" in query:
        try:
            await user.download("spotify")
        except Exception as e:
            logging.error(e)
            await user.sendMessage(
                "Ha ocurrido un error. Vuelve a intentarlo más tarde."
            )
    elif "descargar-youtube-audio" in query:
        try:
            await user.download("youtube")
        except Exception as e:
            logging.error(e)
            await user.sendMessage(
                "Ha ocurrido un error. Vuelve a intentarlo más tarde."
            )
    elif "descargar-youtube-video" in query:
        try:
            await user.download("youtube-video")
        except Exception as e:
            logging.error(e)
            await user.sendMessage(
                "Ha ocurrido un error. Vuelve a intentarlo más tarde."
            )
    elif "descargar-album" in query:
        try:
            await descarga_album(update, context)
        except Exception as e:
            logging.error(e)
            await user.sendMessage(
                "Ha ocurrido un error. Vuelve a intentarlo más tarde."
            )


instruction = "You are a Music Expert assistant you know exatcly how music works, what makes a song a great song, you know what are the most popular songs now, you know every detail about every song ever released. Because you are an apassionate about music, nothing fills your soul more than music.You can download and show songs to the user.  Every time you mention a song, you have to call the function show_song to show the song to the user, you can call this function multiple times to show different songs. Remember every time you mention a song you have to call the function. Not mention a song without calling the function. You arent a objective agent, you have your own opinion about music and what you, although you truly appreciate every gender of music. Always call the function for every song mentioned, dont ask me if may show it, just show it,"

assistant = client.beta.assistants.create(
    name="Music Expert",
    instructions=instruction,
    tools=[
        {
            "type": "function",
            "function": {
                "name": "search_song",
                "description": "Show a song the user, you can call this function multiple times to show different songs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for showing a song, only put in this the name of the song and the name of the artist nothing more. dont: The Best Song of Bad Bunny, do: Monaco - Bad Bunny",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
    ],
    model="gpt-3.5-turbo",
)


async def AI(update, context):
    user = checkstate(update, context)
    thread = user.thread
    # messagge = update.message.text.replace("/ai ", "")

    # Use the new OpenAI Assistant API to generate a response to a user's input let the Assistan call the show_song function
    # message = client.beta.threads.messages.create(
    #     thread_id=thread.id,
    #     role="user",
    #     content=messagge,
    # )

    # get the functions callings from the message
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions=instruction,
    )
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        await asyncio.sleep(1)

    available_functions = {
        "search_song": user.searchSong,
    }

    print(run)
    toolOutput = []
    if run.status == "requires_action":
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = await function_to_call(
                query=function_args.get("query"),
            )
            toolOutput.append(
                {
                    "tool_call_id": tool_call.id,
                    "output": function_response,
                }
            )
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=toolOutput,
        )
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        # sleep a little
        await asyncio.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages)
    # for message in messages.data[0]:
    await user.sendMessage(
        messages.data[0].content[0].text.value,
        disable_web_page_preview=True,
    )


async def radio(update, context):
    ## Es auto contenida no necesita iniciar sesion
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
    ## Es auto contenida no necesita iniciar sesion

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Quitado",
        reply_markup=ReplyKeyboardRemove(),
    )


async def unknown(update, context):
    ## Es auto contenida no necesita iniciar sesion

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
        lambda update, context: checkstate(update, context).searchSong(mode="spotify"),
    )
    app.add_handler(spotify_link_handler)

    youtube_link_handler = MessageHandler(
        filters.TEXT
        & filters.Regex(
            r"(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11})"
        ),
        lambda update, context: checkstate(update, context).searchSong(mode="youtube"),
    )
    app.add_handler(youtube_link_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    app.add_handler(echo_handler)

    # descargar_handler = CommandHandler("descargar", descargar)
    # app.add_handler(descargar_handler)

    spotify = CommandHandler(["spotify", "calidad"], spotifymode)
    app.add_handler(spotify)

    youtubeh = CommandHandler("youtube", youtubemode)
    app.add_handler(youtubeh)
    app.add_handler(CommandHandler(["ai", "ia"], AI))

    # app.add_handler(MessageHandler(Filters.entity('url'), album))

    app.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, audio_handler))

    app.add_handler(CallbackQueryHandler(queryhandler))
    # application.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CommandHandler("recomiendame", recomendacion))

    app.add_handler(CommandHandler("radio", radio))
    app.add_handler(CommandHandler(["help", "ayuda"], help))
    app.add_handler(CommandHandler("album", album))
    app.add_handler(CommandHandler("quitar", quitradiobutton))

    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Se ejecuta la clase y el constructor creara un objeto que se guardará en app

    # app.run_polling(stop_signals=None)

    app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        secret_token="ASecretTokenIHaveChangedByNoww",
        webhook_url="https://my-downloaderbot.fly.dev",
        # webhook_url="https://1b0f-191-88-98-128.ngrok-free.app",
    )


if __name__ == "__main__":
    main()
