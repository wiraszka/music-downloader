from __future__ import unicode_literals
import os
import json
from apiclient.discovery import build
import youtube_dl
import ffmpeg
from config import YOUTUBE_API_KEY
from mutagen import MutagenError
from mutagen.mp3 import MP3


# Input song name
query = input("Search for song here: ")
print(query)

# Youtube API Authentication and generate search request
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
request = youtube.search().list(q=query, part='snippet', type='video', maxResults=5)
results = request.execute()

# List video titles and urls for top 5 search results, then store urls for later use
url_list = []
video_list = []
count = 0
for item in results['items']:
    count += 1
    print(count, item['snippet']['title'])
    video_list.append(item['snippet']['title'])
    id = item['id']['videoId']
    url ='https://www.youtube.com/watch?v=' + id
    print(url)
    url_list.append(url)

# Choose which url to download
choice = int(input('Which song would you like to download? '))
i = choice - 1
chosen_url = url_list[i]
chosen_video = video_list[i]
print('Downloading...', chosen_video, chosen_url)

# Youtube_dl parameters config
download_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'nocheckcertificate': 'True',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Specify output directory for downloads
if not os.path.exists('songs'):
    os.mkdir('songs')
else:
    os.chdir('songs')

# Download song from chosen Youtube url
with youtube_dl.YoutubeDL(download_options) as dl:
    dl.download([chosen_url])

# Create dict containing song information and save to txt file
tags = {
    'video_title' : video_list[i],
    'url' : url_list[i],
    'video_duration' : '',
    'artist' : '',
    'track' : '',
    'mix' : '',
    'featuring' : '',
    'album' : '',
    'album_type' : '',
    'track_number' : '',
    'genre' : '',
    'extra' : '',
    'bpm' : '',
    'duration' : '',
    'bitrate' : '',
    }

# Analyze song for duration and bitrate
audio_file = video_list[i] + '.mp3'
audio_file_path = os.getcwd() + '/' + audio_file
extra_info = MP3(audio_file_path)
tags['video_duration'] = extra_info.info.length
tags['bitrate'] = extra_info.info.bitrate

# Write song info to .txt file
song_info = json.dumps(tags, indent=2)
with open('C:/Users/Adam/Desktop/Projects/music/music-downloader/song-info.txt','w') as txt:
    txt.write(song_info)
