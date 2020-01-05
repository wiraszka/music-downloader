from __future__ import unicode_literals
import os
import ffmpeg
from apiclient.discovery import build
import youtube_dl
import requests
import urllib.request
import spotipy
import spotipy.util as util
from spotipy import oauth2
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, YOUTUBE_API_KEY


# Input song name
query = input("Search for song here: ")
print(query)

# Youtube API Authentication and search request
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
request = youtube.search().list(q=query, part='snippet', type='video', maxResults=5)
results = request.execute()

# List video titles and urls for top 5 results of query, then store urls in list for later use
url_list = []
count = 0
for item in results['items']:
    count += 1
    print(count, item['snippet']['title'])
    id = item['id']['videoId']
    url ='https://www.youtube.com/watch?v=' + id
    print(url)
    url_list.append(url)

# Choose which url to download
choice = int(input('Which song would you like to download? '))
i = choice - 1
chosen_url = url_list[i]
print(chosen_url)

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

# Download song based on chosen Youtube url
with youtube_dl.YoutubeDL(download_options) as dl:
    dl.download([chosen_url])
