import datetime
import eyed3
import ffmpeg
import html
import json
import os
import re
import spotipy
import spotipy.util as util
import urllib.request
import youtube_dl
from apiclient.discovery import build # youtube API
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, YOUTUBE_API_KEY
from fuzzywuzzy import fuzz
from json.decoder import JSONDecodeError
from spotipy import oauth2
from string import printable
from urllib.request import urlopen

def spotify_search(search_query):
    # Get access token for Spotipy API
    token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    cache_token = token.get_access_token()
    spotify = spotipy.Spotify(cache_token)

    # Input song name and search spotify
    print('Searching for:', search_query)
    result = spotify.search(search_query, limit=13)
    spotify_summary = None
    #print(json.loads(result, indent=2)

    # Check if search successful
    if len(result['tracks']['items']) < 1:
        print('Spotify search failed')
        search_success = False
    else:
        print('Spotify search successful')
        search_success = True

    # If spotify search successful, return relevant song info for top-10 results in json format
    if search_success == True:
        song_info = []
        count = 0
        for song in result['tracks']['items']:
            count += 1
            tags = {}
            tags['id'] = count
            tags['artist'] = song['artists'][0]['name']
            tags['track'] = song['name']
            tags['album'] = song['album']['name']
            tags['album_artist'] = song['album']['artists'][0]['name']
            tags['album_type'] = song['album']['album_type']
            tags['album_art'] = song['album']['images'][0]['url']
            tags['year'] = song['album']['release_date'][:4]
            tags['track_number'] = song['track_number']
            tags['total_tracks'] = song['album']['total_tracks']
            tags['duration_s'] = int(song['duration_ms']) / 1000
            tags['duration'] = str(datetime.timedelta(seconds=tags['duration_s'])).split('.')[0]
            print(tags['id'], '-', tags['artist'], '-', tags['track'], '- album:', tags['album'], '- duration:', tags['duration'])
            song_info.append(tags)
        spotify_summary = json.dumps(song_info, indent=2)
    #print(spotify_summary)
    return spotify_summary, search_success
