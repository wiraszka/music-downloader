import os
import sys
import json
import pprint
import requests
import urllib.request
import spotipy
import spotipy.util as util
from spotipy import oauth2
from json.decoder import JSONDecodeError
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET


txt = 'C:/Users/Adam/Desktop/Projects/music/music-downloader/song-info.txt'

## AUTHENTICATION USING OAUTH
# Client_key and Secret_key saved in config.py
token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)

# Get access token
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token)

def check_json(txt):
# Open txt file and check json containing song info
    with open(txt, 'r') as j:
        contents = j.read()
        if len(contents) < 1:
            print('txt file does not exist or in wrong directory')
        else:
            print(contents)
        return contents

def dl_album_cover(album_cover):
    filename = 'img{}.png'.format(i)
    print(filename)
    response = urllib.request.urlretrieve(album_cover, filename)
    if response.status_code == 200:
        try:
            album_dump = 'C:/Users/Adam/Desktop/Projects/music/album-dump/'
            with open(album_dump, 'wb') as f:
                f.write(response.content)
        except:
            print('Could not download image')
    else:
        print('Server error')
    return filename






# Initial sanity check
check_json(txt)
# Open and read json file containing song names
with open(txt, 'r') as j:
    song = json.loads(j.read())
# Generate search string
    try_number = 1
    print('Attempt',try_number)
    if try_number == 1:
        search_str = song['video_title']
        i = 0
# Search for song (search string) using spotify API
    print('Searching for...', search_str)
    result = spotify.search(search_str, limit=5)
    #pprint.pprint(result)
# Check if search unsuccessful
    if len(result['tracks']['items']) < 1:
        print('Search query failed for:', search_str)
    else:
        print('search successful')
        artist = result['tracks']['items'][i]['artists'][0]['name']
        print('artist is:', artist)
        album = result['tracks']['items'][i]['album']['name']
        print('album is:', album)
        album_type = result['tracks']['items'][i]['album']['album_type']
        print('album type is:', album_type)
        track = result['tracks']['items'][i]['name']
        print('track is:', track)
        track_number = result['tracks']['items'][i]['track_number']
        print('track number is:', track_number)
        duration_ms = result['tracks']['items'][i]['duration_ms']
        duration_s = duration_ms / 1000
        print('duration is:', duration_s)

# If successful, call album_cover_download function to dl album art
    try:
        album_cover = result['tracks']['items'][i]['album']['images'][0]['url']
        print('Image link is:', album_cover)
        dl_album_cover(album_cover)
    except:
        album_cover = ""
        print("Image indexing error for:", search_str)
        #pprint.pprint(result)

# Compare duration of audio file to Spotify search result
duration_min = song['duration'] - 3
duration_max = song['duration'] + 3
if duration_min <= duration_s <= duration_max:
    print('Song duration in Spotify search matches audio file duration')
else:
    print('Song duration in Spotify search DOES NOT match audio file duration')
    i += 1
