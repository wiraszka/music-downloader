import eyed3
import ffmpeg
import os
import urllib.request
import youtube_dl



def dl_song(chosen_url, output_directory):
    # Go to output directory
    os.chdir(output_directory)

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

    # Download audio from Youtube url
    with youtube_dl.YoutubeDL(download_options) as dl:
        audio_filename = dl.prepare_filename(dl.extract_info(chosen_url))
        audio_filename = audio_filename.replace('.webm', '.mp3')
    return audio_filename


def my_hook(d):
    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        print("Done downloading {}".format(file_tuple[1]))
    if d['status'] == 'downloading':
        print(d['filename'], d['_percent_str'], d['_eta_str'])


def dl_cover_art(index, spotify_summary, cover_art_directory, root_directory):
    # Download cover art
    os.chdir(cover_art_directory)
    if os.path.exists(f'img{index}.png'):
        os.remove(f'img{index}.png')
    image_file = f'img{index}.png'.format(0)
    response = urllib.request.urlretrieve(spotify_summary[index]['album_art'], image_file)
    os.chdir(root_directory)


def apply_ID3_tags(index, spotify_summary, output_filename, root_directory, downloading, output_directory, cover_art_directory):
    os.chdir(output_directory)

    # Rename audio file to "temp.mp3", since file might have non-ascii characters (eyed3 cannot handle these)
    if os.path.exists('temp.mp3'):
        os.remove('temp.mp3')

    # Downloading = True, during initial download phase (before confirmation screen)
    if downloading == True:
        os.rename(output_filename, 'temp.mp3')
        apply_tags = eyed3.load('temp.mp3')
    elif downloading == False:
        apply_tags = eyed3.load(output_filename)

    # Initialize tags for audio file, then apply new media tags
    apply_tags.initTag()
    cover_art_image = cover_art_directory + '/' + f'img{index}.png'
    apply_tags.tag.images.set(3, open(cover_art_image, 'rb').read(), 'image/png')
    apply_tags.tag.artist = spotify_summary[index]['artist']
    apply_tags.tag.title = spotify_summary[index]['track']
    apply_tags.tag.album = spotify_summary[index]['album']
    apply_tags.tag.album_artist = spotify_summary[index]['album_artist']
    apply_tags.tag.recording_date = spotify_summary[index]['year']
    apply_tags.tag.track_num = spotify_summary[index]['track_number']
    try:
        apply_tags.tag.genre = spotify_summary[index]['genre']
    except:
        print('No genre information to add.')
    apply_tags.tag.save()


    # Rename audio file from "temp.mp3" (before confirmation screen)
    if downloading == True:
        os.rename('temp.mp3', output_filename)
    # Rename audio file to match spotify song info: Artist - Track (after confirmation screen)
    elif downloading == False:
        formatted_filename = spotify_summary[index]['artist'] + ' - ' + spotify_summary[index]['track'] + '.mp3'
        os.rename(output_filename, formatted_filename)
        print('Filename:', formatted_filename)

    # Delete cover art image from output folder
    if os.path.exists(f'img{index}.png'):
        os.remove(f'img{index}.png')
    os.chdir(root_directory)
