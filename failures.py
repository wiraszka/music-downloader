import os
import json
from json.decoder import JSONDecodeError

music_path = "C:/Users/Adam/Documents/Adams Music2"
manifest = "C:/Users/Adam/Documents/Adams Music2/manifest.txt"
#path = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/sample-music2'
dir_path = "C:/Users/Adam/Desktop/Projects/music/music-organizer"

os.chdir(music_path)
if not os.path.exists('Errors'):
    os.mkdir('Errors')
    os.cd('Errors')
    os.mkdir('song_reformat_errors')
    os.mkdir('music_update_errors')

os.chdir(music_path)
with open('manifest.txt', 'r') as manifest:
    manifest = json.loads(manifest.read())
print(manifest)
