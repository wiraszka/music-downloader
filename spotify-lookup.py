import os
import sys
import json
import pprint
import requests
import urllib.request
import eyed3
import spotipy
import spotipy.util as util
from spotipy import oauth2
from json.decoder import JSONDecodeError
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET


txt = 'C:/Users/Adam/Desktop/Projects/music/music-downloader/song-info.txt'

# Get access token for Spotipy
# Client_key and Secret_key saved in config.py
token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token)

def check_json(txt):
# Check whether txt file exists and is in the correct directory
    with open(txt, 'r') as j:
        contents = j.read()
        if len(contents) < 1:
            print('txt file does not exist or in wrong directory')
        else:
            print(contents)
        return contents

def get_spotify_info(result, song, i):
    song['artist'] = result['tracks']['items'][i]['artists'][0]['name']
    song['album'] = result['tracks']['items'][i]['album']['name']
    song['album_type'] = result['tracks']['items'][i]['album']['album_type']
    song['track'] = result['tracks']['items'][i]['name']
    song['track_number'] = result['tracks']['items'][i]['track_number']
    duration_ms = result['tracks']['items'][i]['duration_ms']
    song['duration'] = duration_ms / 1000
    print(song)

    return song

def compare_duration(song, i, duration_match):
# Compare duration of audio file to Spotify search result (+/- 5 seconds)
    if song['video_duration'] - 5 <= song['duration'] <= song['video_duration'] + 5:
        print('Success. Song duration in Spotify search matches audio file duration')
        duration_match = True
        print(duration_match)
        return duration_match
    else:
        print('Song duration in Spotify search DOES NOT match audio file duration')
        i += 1
        print(duration_match, i)
        return i

def dl_album_cover(result, i):
# Find cover art url from Spotify
    try:
        album_cover_url = result['tracks']['items'][i]['album']['images'][0]['url']
        print('Cover album link is:', album_cover_url)
    except:
        print("Image indexing error for:", search_str)
# Download cover art
    os.chdir('songs')
    if os.path.exists('img.png'):
        os.remove('img.png')
    image_file = 'img.png'.format(i)
    response = urllib.request.urlretrieve(album_cover_url, image_file)
    os.chdir('../')
    return image_file

def apply_album_art(song):
    os.chdir('songs')
    audio_file = song['video_title'] + '.mp3'
    apply = eyed3.load(audio_file)
    apply.initTag()
    apply.tag.images.set(3, open('img.png','rb').read(), 'image/png')
    apply.tag.save()
    print('Album art applied to audio file')
    os.chdir('../')


def apply_metadata():
    pass

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
# Search for song (search string) using spotify API
    print('Searching for...', search_str)
    result = spotify.search(search_str, limit=5)
    #pprint.pprint(result)

# Check if search successful
    if len(result['tracks']['items']) < 1:
        print('Search query failed for:', search_str)
    else:
        print('Search successful')

# Check if duration of downloaded audio matches duration of Spotify songs
duration_match = False
i = 0
while duration_match == False:
    get_spotify_info(result, song, i)
    song = song
    compare_duration(song, i, duration_match)
    i += 1
    if duration_match == True:
        print('Downloading cover art...')
        dl_album_cover(result, i)
        break
    if i == 5:
        print('Could not match audio length on Spotify')
        break

# If duration check fails, download album art from first spotify search item
if duration_match == False:
    i = 0
    dl_album_cover(result, i)

# Apply metadata from Spotify to mp3 file

# Apply downloaded cover art to mp3 file
apply_album_art(song)

#pprint.pprint(result)
