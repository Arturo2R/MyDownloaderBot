from pytube import YouTube

def descargayoutube(url, type:"audio"or"video"="audio"):
  song = YouTube(url)
  try:
			if type == "audio":
				streams = song.streams.filter(type=type, audio_codec='opus').order_by('abr').last()
			if type== "video":
				streams = song.streams.filter(type=type, video_codec='vp9').last()
  except:
    	streams = song.streams.filter(type=type).order_by('abr').last()
  finally: 
			print(streams)
			file = streams.download()
			print( streams
					)
			file_title = song.title
			file_author = song.author
			
			print(file)
			print(song)

  return file_title, file 

descargayoutube("https://www.youtube.com/watch?v=F4neLJQC1_E", "video")