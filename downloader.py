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
from apiclient.discovery import build  # youtube API
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, YOUTUBE_API_KEY
from fuzzywuzzy import fuzz
from json.decoder import JSONDecodeError
from spotipy import oauth2
from string import printable
from urllib.request import urlopen


def spotify_search(search_query):
    # Get access token for Spotipy API
    token = util.oauth2.SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    cache_token = token.get_access_token()
    spotify = spotipy.Spotify(cache_token)

    # Input song name and search spotify
    print('Searching for:', search_query)
    result = spotify.search(search_query, limit=7)
    spotify_summary = None
    # print(json.loads(result, indent=2)

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
            print(tags['id'], '-', tags['artist'], '-', tags['track'],
                  '- album:', tags['album'], '- duration:', tags['duration'])
            song_info.append(tags)
        spotify_summary = json.dumps(song_info, indent=2)
    # print(spotify_summary)
    return spotify_summary, search_success


def center_text(longer, shorter, amount, order):
    half = int(round(amount / 1.5))
    shorter = ' '*half + shorter
    if order:
        centered = longer + '\n' + shorter
    else:
        centered = shorter + '\n' + longer
    return centered


def remove_extra_info(split_text):
    mod_text = []
    for line in split_text:
        if len(line) > 68:  # 69 characters fit into display space
            if '(' in line:
                # Remove all characters between () and []
                line = re.sub("[\(\[].*?[\)\]]", "", line)
        mod_text.append(line)
    print(mod_text)
    return mod_text


def modify_text(display_text):
    split_text = display_text.split('\n')
    split_text = remove_extra_info(split_text)
    len_line1 = len(split_text[0])
    len_line2 = len(split_text[1])
    amount = abs(len_line1 - len_line2)
    if len_line1 > len_line2:
        order = True
        centered = center_text(split_text[0], split_text[1], amount, order)
    elif len_line2 > len_line1:
        order = False
        centered = center_text(split_text[1], split_text[0], amount, order)
    elif len_line1 == len_line2:
        centered = display_text
    return centered


def search_youtube(search_str):
    # Youtube API Authentication and generate search request
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=search_str, part='snippet', type='video', maxResults=10)
    results = request.execute()
    # Return video title and url for each result
    youtube_results = []
    print('Searching Youtube for:', search_str)
    for item in results['items']:
        info = {}
        info['vid_title'] = html.unescape(item['snippet']['title'])
        info['url'] = 'https://www.youtube.com/watch?v=' + item['id']['videoId']
        #print('Analyzing:', info['vid_title'], info['url'])
        # Get video durations and append to youtube_results
        video_id = item['id']['videoId']
        searchUrl = "https://www.googleapis.com/youtube/v3/videos?id=" + \
            video_id+"&key="+YOUTUBE_API_KEY+"&part=contentDetails"
        response = urllib.request.urlopen(searchUrl).read()
        data = json.loads(response)
        duration = data['items'][0]['contentDetails']['duration']
        duration = re.findall('\d+', duration)
        info['duration_s'] = int(duration[0]) * 60
        try:
            info['duration_s'] = info['duration_s'] + int(duration[1])
        except:
            pass
        info['duration'] = str(datetime.timedelta(seconds=info['duration_s'])).split('.')[0]
        # print(info['duration'])
        youtube_results.append(info)
    return youtube_results


def filter_entries(search_str, item):
    '''Remove videos such as covers, live recordingss/performances
    unless explicitly asked for in search string'''
    disallowed = False
    print('-' * 80)
    print('Analyzing:', item['vid_title'], item['duration'])
    if 'cover' not in search_str:
        if 'cover' in item['vid_title'].lower():
            print('DISALLOWED due to cover')
            disallowed = True
    if 'live' not in search_str:
        if 'live' in item['vid_title'].lower():
            print('DISALLOWED due to live')
            disallowed = True
    return disallowed


def match_string_only(search_str, youtube_results):
    matched = False
    vid_list = {'highest_match': 0}
    for item in youtube_results:
        disallowed = filter_entries(search_str, item)
        if disallowed:
            continue
        match_score = fuzz.ratio(item['vid_title'], search_str)
        print('Fuzzy score:', match_score)
        item['fuzzy_score'] = match_score
        if match_score > vid_list['highest_match']:
            vid_list['best_vid'] = item['vid_title']
            vid_list['best_url'] = item['url']
            vid_list['highest_match'] = match_score
        #print('current best match is:', vid_list)
        if match_score > 95:
            matched = True
            chosen_url = item['url']
            chosen_video = item['vid_title']
    if matched == False:
        chosen_url = vid_list['best_url']
        chosen_video = vid_list['best_vid']
    print('=' * 80)
    print('Chosen download link:', chosen_video)
    print('=' * 80)
    return chosen_url, chosen_video


def match_audio(search_str, spotify_summary, youtube_results, index):
    matched = False
    vid_list = {'highest_match': 0}
    for item in youtube_results:
        disallowed = filter_entries(search_str, item)
        if disallowed:
            continue
        # Score youtube results based on duration match
        duration_diff = abs(spotify_summary[index]['duration_s'] -
                            item['duration_s'])  # calculate time difference
        duration_score = 0.35 * (100 - duration_diff)  # perfect time match is 35 points
        print('Duration difference:', duration_diff)
        print('Duration score:', duration_score)

        # Use fuzzy matching to score similarity between search string and youtube titles
        match_ratio = fuzz.ratio(item['vid_title'], search_str)
        match_score = match_ratio*0.65 + duration_score  # perfect fuzzy match is 65 points
        print('Fuzzy score:', match_ratio)
        print('Final matching score:', match_score)

        item['duration_diff'] = duration_diff
        item['fuzzy_score'] = match_score

        # Choose video if length is within 1 sec and fuzzy match above 65
        if duration_diff < 1.2 and match_ratio > 65:
            chosen_url = item['url']
            chosen_video = item['vid_title']
            print('MATCHED EARLY')
            return chosen_url, chosen_video

        # Keep track of best youtube result in a dict
        if match_score > vid_list['highest_match']:
            vid_list['best_vid'] = item['vid_title']
            vid_list['best_url'] = item['url']
            vid_list['highest_match'] = match_score
        #print('current best match is:', vid_list)
        if match_score > 95:
            matched = True
            chosen_url = item['url']
            chosen_video = item['vid_title']
    if matched == False:
        chosen_url = vid_list['best_url']
        chosen_video = vid_list['best_vid']
    print('=' * 80)
    print('Chosen download link:', chosen_video)
    print('=' * 80)
    return chosen_url, chosen_video


def dl_song(chosen_url, output_directory):
    # Youtube_dl parameters config
    download_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'nocheckcertificate': 'True',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    # Go to output directory
    os.chdir(output_directory)
    #print('cwd is:', os.getcwd())

    # Download song from chosen Youtube url
    with youtube_dl.YoutubeDL(download_options) as dl:
        audio_filename = dl.prepare_filename(dl.extract_info(chosen_url))
        audio_filename = audio_filename.replace('.m4a', '.mp3')
        audio_filename = audio_filename.replace('.webm', '.mp3')
        # dl.download([chosen_url])
        print('filename is:', audio_filename)
    return audio_filename


def dl_cover_art(index, spotify_summary):
    # Download cover art
    if os.path.exists(f'img{index}.png'):
        os.remove(f'img{index}.png')
    image_file = f'img{index}.png'.format(0)
    response = urllib.request.urlretrieve(spotify_summary[index]['album_art'], image_file)


def apply_ID3_tags(index, spotify_summary, audio_filename, output_filename, root_directory, downloading, output_directory):
    # Rename audio file to 'temp.mp3' because file might have non-ascii characters (eyed3 cannot handle these)
    if os.path.exists('temp.mp3'):
        os.remove('temp.mp3')
        print('removed ')
    if downloading == True:
        os.rename(audio_filename, 'temp.mp3')
        apply_tags = eyed3.load('temp.mp3')
    else:
        os.chdir(output_directory)
        apply_tags = eyed3.load(output_filename)
    apply_tags.initTag()
    apply_tags.tag.images.set(3, open(f'img{index}.png', 'rb').read(), 'image/png')
    apply_tags.tag.artist = spotify_summary[index]['artist']
    apply_tags.tag.title = spotify_summary[index]['track']
    apply_tags.tag.album = spotify_summary[index]['album']
    apply_tags.tag.album_artist = spotify_summary[index]['album_artist']
    apply_tags.tag.recording_date = spotify_summary[index]['year']
    apply_tags.tag.track_num = spotify_summary[index]['track_number']
    try:
        apply_tags.tag.genre = spotify_summary[index]['genre']
    except:
        print('no genre')
    apply_tags.tag.save()
    print('Media tags and album art applied to audio file')
    if downloading == True:
        os.rename('temp.mp3', output_filename)
    os.chdir(root_directory)
