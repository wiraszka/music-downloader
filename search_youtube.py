import datetime
import html
import json
import re
import urllib.request
from urllib.request import urlopen
from googleapiclient.discovery import build  # youtube API
from config import YOUTUBE_API_KEY
from fuzzywuzzy import fuzz

def search_yt(search_str):
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
        # Filter youtube results to remove covers, live recordings, etc.
        disallowed = filter_entries(search_str, item)
        if disallowed:
            continue
        # Score remaining youtube results based on duration match
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

        # Keep track of best youtube result in a dict
        if match_score > vid_list['highest_match']:
            vid_list['best_vid'] = item['vid_title']
            vid_list['best_url'] = item['url']
            vid_list['highest_match'] = match_score

        # Choose video if length is within 1 sec and fuzzy match above 65
        if duration_diff < 1.2 and match_ratio > 65:
            chosen_url = item['url']
            chosen_video = item['vid_title']
            print('MATCHED EARLY')
            return chosen_url, chosen_video

        # Choose video if total match score above 95
        if match_score > 95:
            matched = True
            chosen_url = item['url']
            chosen_video = item['vid_title']

    # If no video crosses threshold for automatic selection, choose "best" url from vid_list
    if matched == False:
        chosen_url = vid_list['best_url']
        chosen_video = vid_list['best_vid']
    print('=' * 80)
    print('Chosen download link:', chosen_video)
    print('=' * 80)
    return chosen_url, chosen_video
