import os
import re
import json
import urllib.request
from urllib.request import urlopen
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



def spotify_search(search_query):
# Get access token for Spotipy API (Client_key and Secret_key imported from config.py)
    token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    cache_token = token.get_access_token()
    spotify = spotipy.Spotify(cache_token)

# Input song name and search spotify
    print('Searching for...', search_query)
    result = spotify.search(search_query, limit=10)
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
            print(tags['id'], '-', tags['artist'], '-', tags['track'], '- album:', tags['album'], '- duration:', tags['duration_s'])
            song_info.append(tags)
        spotify_summary = json.dumps(song_info, indent=2)
    #print(spotify_summary)
    return spotify_summary, search_success


def search_youtube(search_success, search_str):
# Youtube API Authentication and generate search request
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=search_str, part='snippet', type='video', maxResults=10)
    results = request.execute()
# Return video title and url for each result
    youtube_results = []
    for item in results['items']:
        info = {}
        info['vid_title'] = html.unescape(item['snippet']['title'])
        info['url'] ='https://www.youtube.com/watch?v=' + item['id']['videoId']
        #print('Analyzing:', info['vid_title'], info['url'])
    #print(youtube_results)
# Get video durations and append to youtube_results
        video_id = item['id']['videoId']
        searchUrl = "https://www.googleapis.com/youtube/v3/videos?id="+video_id+"&key="+YOUTUBE_API_KEY+"&part=contentDetails"
        response = urllib.request.urlopen(searchUrl).read()
        data = json.loads(response)
        duration = data['items'][0]['contentDetails']['duration']
        duration = re.findall('\d+', duration)
        info['duration'] = int(duration[0]) * 60
        try:
            info['duration'] = info['duration'] + int(duration[1])
        except:
            pass
        #print(info['duration'])
        youtube_results.append(info)
    return youtube_results


def match_audio(search_str, spotify_summary, youtube_results, index):
    matched = False
    vid_list = {
        'best_vid' : '',
        'best_url' : '',
        'highest_match' : 0
        }
    for item in youtube_results:
# Remove videos such as covers, live recordings, performances unless explicitly asked for
        print('Analyzing:', item['vid_title'], item['duration'])
        if 'cover' in item['vid_title'].lower():
            print('DISALLOWED')
            continue
        if 'live' in item['vid_title'].lower():
            print('DISALLOWED')
            continue
# Remove videos that don't match length of target song on spotify
        try:
            lower_limit = int(spotify_summary[index]['duration_s']) - 5
            upper_limit = int(spotify_summary[index]['duration_s']) + 5
            print(lower_limit, item['duration'], upper_limit)
            if not lower_limit < item['duration'] < upper_limit:
                print('Duration mismatch')
                continue
        except:
            pass

# Use fuzzy matching to find closest match between search string and remaining search results
        match_ratio = fuzz.ratio(item['vid_title'], search_str)
        print('Match ratio:', match_ratio)
        if match_ratio > vid_list['highest_match']:
            vid_list['best_vid'] = item['vid_title']
            vid_list['best_url'] = item['url']
            vid_list['highest_match'] = match_ratio
        #print('current best match is:', vid_list)
        if match_ratio > 85:
            matched = True
            chosen_url = item['url']
            chosen_video = item['vid_title']
    if matched == False:
        chosen_url = vid_list['best_url']
        chosen_video = vid_list['best_vid']
        print(chosen_video)
    return chosen_url


def dl_song(chosen_url):
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
        audio_filename = dl.prepare_filename(dl.extract_info(chosen_url))
        audio_filename = audio_filename.replace('.webm', '.mp3')
        #dl.download([chosen_url])
        print('filename is:', audio_filename)
    return audio_filename


def dl_cover_art(index, spotify_summary):
# Download cover art
    if os.path.exists('img.png'):
        os.remove('img.png')
    image_file = 'img.png'.format(0)
    response = urllib.request.urlretrieve(spotify_summary[index]['album_art'], image_file)

def apply_ID3_tags(index, spotify_summary, audio_filename, output_filename):
# Rename audio file to 'temp.mp3' because file might have non-ascii characters (eyed3 cannot handle these)
    try:
        if os.path.exists('temp.mp3'):
            os.remove('temp.mp3')
        os.rename(audio_filename, 'temp.mp3')
        apply_tags = eyed3.load('temp.mp3')
        apply_tags.initTag()
        apply_tags.tag.images.set(3, open('img.png','rb').read(), 'image/png')
        apply_tags.tag.artist = spotify_summary[index]['artist']
        apply_tags.tag.title = spotify_summary[index]['track']
        apply_tags.tag.album = spotify_summary[index]['album']
        apply_tags.tag.album_artist = spotify_summary[index]['album_artist']
        apply_tags.tag.recording_date = spotify_summary[index]['year']
        apply_tags.tag.track_num = spotify_summary[index]['track_number']
        apply_tags.tag.save()
        print('Media tags and album art applied to audio file')
        os.rename('temp.mp3', output_filename)
    except:
        print('Could not apply media tags to file')
    os.chdir('../')


# START HERE
# User inputs song they want to download
search_query = input("Input song you want to download: ")
spotify_summary = spotify_search(search_query)
search_success = spotify_summary[1]

# If spotify search comes up with results, prompt user to choose best result
if search_success == True:
    spotify_summary = json.loads(spotify_summary[0])
    try:
        index = int(input('Input audio file you would like to download: ')) - 1
        if index not in range(len(spotify_summary)):
            print('try again')
            quit()
    except:
        quit()

# Generate search string for Youtube search from spotify result or from initial user search
if search_success == True:
    search_str = spotify_summary[index]['artist'] + ' - ' + spotify_summary[index]['track']
elif search_success == False:
    search_str = search_query
    index = 0
print('Finding download link for:', search_str)
youtube_results = search_youtube(search_success, search_str)
chosen_url = match_audio(search_str, spotify_summary, youtube_results, index)
audio_filename = dl_song(chosen_url)

if search_success == True:
    output_filename = spotify_summary[index]['artist'] + ' - ' + spotify_summary[index]['track'] + '.mp3'
    dl_cover_art(index, spotify_summary)
    apply_ID3_tags(index, spotify_summary, audio_filename, output_filename)
else:
    print('Could not find audio tags or album art')
