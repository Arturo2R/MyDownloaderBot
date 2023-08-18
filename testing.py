from pytube import YouTube

def descargayoutube(url, type:"audio"or"video"="audio"):
  song = YouTube(url) 
  streams = song.streams.filter(type=type).order_by('abr').last()
  print(streams)
  # file = streams.download()
  # return file

descargayoutube("https://www.youtube.com/watch?v=xfLom4iv2GE")