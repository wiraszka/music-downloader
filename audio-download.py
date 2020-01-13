import os
import json
import urllib.request
import eyed3
import spotipy
import spotipy.util as util
from spotipy import oauth2
from json.decoder import JSONDecodeError
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, YOUTUBE_API_KEY
from apiclient.discovery import build
import youtube_dl
import ffmpeg
import html
from fuzzywuzzy import fuzz
from string import printable



# Get access token for Spotipy
# Client_key and Secret_key saved in config.py
token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token)

# Input song name and search spotify
def spotify_search(search_query):
    print('Searching for...', search_query)
    result = spotify.search(search_query, limit=5)
    global search_success
    #print(json.loads(result, indent=2)

# Check if search successful
    if len(result['tracks']['items']) < 1:
        print('Search failed')
        search_success = False
    else:
        print('Search successful')
        search_success = True

# List top 5 search results, then return all important song info in json format
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
            print(tags['year'])
            print(tags['id'], '-', tags['artist'], '-', tags['track'], '-', tags['album'], '-', tags['duration_s'], tags['album_art'])
            song_info.append(tags)
        global search_summary
        search_summary = json.dumps(song_info, indent=2)
    return search_summary, search_success



def search_youtube(index, search_success, search_query):
# Generate search string from spotify song information, format: 'artist - track'
    if search_success == True:
        search_str = search_summary[index]['artist'] + ' - ' + search_summary[index]['track']
        print('Finding download link for:', search_str)
    elif search_success == False:
        search_str = search_query
# Youtube API Authentication and generate search request
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=search_str, part='snippet', type='video', maxResults=10)
    results = request.execute()

# Find closest match (>90%) between 'search_str' and youtube search results using fuzzy matching
    global audio_file
    matched = False
    vid_list = {
        'best_vid' : '',
        'best_url' : '',
        'highest_match' : 0
        }
    for item in results['items']:
        vid_title = html.unescape(item['snippet']['title'])
        url ='https://www.youtube.com/watch?v=' + item['id']['videoId']
        print('Analyzing:', vid_title, url)
        match_ratio = fuzz.ratio(vid_title, search_str)
        print('Match ratio:', match_ratio)
        if match_ratio > vid_list['highest_match']:
            vid_list['best_vid'] = vid_title
            vid_list['best_url'] = url
            vid_list['highest_match'] = match_ratio
        #print('current best match is:', vid_list)
        if match_ratio > 90:
            matched = True
            chosen_url = url
            chosen_video = vid_title
            audio_file = vid_title + '.mp3'
            break
        else:
            continue
    if matched == False:
        chosen_url = vid_list['best_url']
        chosen_video = vid_list['best_vid']
        audio_file = vid_list['best_vid'] + '.mp3'

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


def dl_cover_art(index):
# Download cover art
    if os.path.exists('img.png'):
        os.remove('img.png')
    image_file = 'img.png'.format(0)
    response = urllib.request.urlretrieve(search_summary[index]['album_art'], image_file)
    return image_file

def apply_ID3_tags(audio_file, special_characters, search_summary, index):
    if special_characters == True:
        original_audio_file = audio_file
        audio_file = 'temp.mp3'
    try:
        apply_tags = eyed3.load(audio_file)
        apply_tags.initTag()
        apply_tags.tag.images.set(3, open('img.png','rb').read(), 'image/png')
        print('Album art applied to audio file')
        apply_tags.tag.artist = search_summary[index]['artist']
        apply_tags.tag.title = search_summary[index]['track']
        apply_tags.tag.album = search_summary[index]['album']
        apply_tags.tag.album_artist = search_summary[index]['album_artist']
        apply_tags.tag.recording_date = search_summary[index]['year']
        apply_tags.tag.track_num = search_summary[index]['track_number']
        apply_tags.tag.save()
        print('Audio tags applied to audio file')
        os.rename('temp.mp3', original_audio_file)
        os.chdir('../')
    except:
        print('Could not apply album art')


# __init__ (lol)
search_query = input("Input song you want to download: ")
spotify_search(search_query)
search_summary = json.loads(search_summary)
user_choice = int(input('Pick best match (1-5): '))
index = user_choice - 1
search_youtube(index, search_success, search_query)
if search_success == True:
    dl_cover_art(index)
# Since eyed3 cannot handle non-ascii, check if they exist in filename, if so then rename and call function again on renamed filename
    special_characters = False
    if set(audio_file).difference(printable):
        print('Filename has special characters, temporarily renaming file')
        os.rename(audio_file, 'temp.mp3')
        special_characters = True

    apply_ID3_tags(audio_file, special_characters, search_summary, index)
else:
    print('Could not find audio tags or album art')
