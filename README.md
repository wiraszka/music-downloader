## MUSIC DOWNLOADER
Download any song from Youtube

Changes:
# Jan 8 2020
- Changes to general flow:
- search spotify API first!
- this will allow pulling of song details and album art directly and accurately
- After spotify match is confirmed by user, THEN search Youtube API for videos matching 'artist - title' format pulled from spotify result
        - this will eliminate need to excessive formatting of youtube video titles, detect valid songs, and add ability to remove unwanted youtube search results (live sets, covers)
        - this will also allow to pull metadata tags and album art directly from spotify result and makes sure it matches what user wanted to find


# 1) audio-download.py
- user inputs a song they would like to download
- script will use Youtube API to list top-5 closest (high-quality) search results
- user chooses which of the search results to download
- script will download the audio from the chosen video and save it in local directory named 'songs'
- user can choose to end process here, or continue and fetch song info (audio tags and album cover) from Spotify API

# 2) spotify-lookup.py
- takes original user input from music-downloader.py and searches Spotify API for song info
- if song is found on Spotify, script adds corresponding audio tags to mp3 file along with album art

# 3) song-reformat.py
- this script runs if no result is found when searching Spotify API using original user input in spotify-lookup.py
- takes json file containing search info (video_title & url) from music-downloader.py
- script analyzes audio file for song duration and bitrate
- script reformats video-title to facilitate search on spotify:
        - removes extra song title information that might cause search to fail (such as: official video, )
        - detects mix type (remix, original mix, mashup, radio edit, etc.)
        - detects featured artists
        - detects and removes weird characters
