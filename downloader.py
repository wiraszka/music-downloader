import eyed3
import ffmpeg
import os
import pafy
import re
import urllib.request
import youtube_dl


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





def dl_song(chosen_url, output_directory):

    # Go to output directory
    os.chdir(output_directory)

    # Download audio from Youtube url
    video = pafy.new(chosen_url)
    webm_filename = video.title + 'webm'
    audio_filename = video.title + 'mp3'
    best_audio = video.getbestaudio()
    print("Bitrate:", best_audio.bitrate)
    best_audio.download()


    # Convert webm to mp3
    input = ffmpeg.input(webm_filename)
    output = ffmpeg.output(audio_filename)
    return audio_filename


def my_hook(d):
    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        print("Done downloading {}".format(file_tuple[1]))
    if d['status'] == 'downloading':
        print(d['filename'], d['_percent_str'], d['_eta_str'])


def dl_cover_art(index, spotify_summary):
    # Download cover art
    if os.path.exists(f'img{index}.png'):
        os.remove(f'img{index}.png')
    image_file = f'img{index}.png'.format(0)
    response = urllib.request.urlretrieve(spotify_summary[index]['album_art'], image_file)


def apply_ID3_tags(index, spotify_summary, audio_filename, output_filename, root_directory, downloading, output_directory):
    os.chdir(output_directory)
    # Rename audio file to "temp.mp3", since file might have non-ascii characters (eyed3 cannot handle these)
    if os.path.exists('temp.mp3'):
        os.remove('temp.mp3')
        print('removed ')
    # True during initial download
    if downloading == True:
        os.rename(audio_filename, 'temp.mp3')
        apply_tags = eyed3.load('temp.mp3')
    # False during final confirmation
    elif downloading == False:
        apply_tags = eyed3.load(output_filename)
    apply_tags.initTag()
    cover_art_image = root_directory + '/' + f'img{index}.png'
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
        print('no genre')
    apply_tags.tag.save()
    # Rename audio file from "temp.mp3"
    if downloading == True:
        os.rename('temp.mp3', output_filename)
    print('Media tags and album art applied to audio file')
    # Delete cover art image from output folder
    if os.path.exists(f'img{index}.png'):
        os.remove(f'img{index}.png')
    os.chdir(root_directory)


# chosen_url = 'https://www.youtube.com/watch?v=lI2CYUUdwwQ'
# output_directory = 'C:/Users/Adam/Desktop/songs'
# audio_filename = dl_song(chosen_url, output_directory)
# progress = my_hook(d)
# print(progress)
