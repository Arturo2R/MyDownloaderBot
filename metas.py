import mutagen
import requests
import youtube-dl

def downloading(url, filename):
  print('Download Starting')
  r = request.get(url)

  with open(filename,'wb') as output_file:
      output_file.write(r.content)

  print('Download Completed!!!')