import os
import youtube_dl
import threading

# TODO: This doesn't seem like an efficient way to get app.config, but...
# from project import app
# from flask.config import Config


# TODO: This feels bad man - Would prefer this function in Downloader class
def my_hook(d):

    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        file_name = file_tuple[1]
        update_song.percent_complete = "100%"
        update_song.completed = True
        print("Done downloading {}".format(file_name))

    if d['status'] == 'downloading':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        file_name = file_tuple[1]
        update_song = song_file_dao.get_song_file_by_file_name(file_name)
        update_song.percent_complete = d['_percent_str']
        song_file_dao.update_song_file(update_song)
        print("{} {} {}".format(d['filename'], d['_percent_str'], d['_eta_str']))


class Downloader(object):

    format_ext = 'mp4'

    def check_youtube(self, url):
        ydl = youtube_dl.YoutubeDL(
            {'outtmpl': '%(id)s%(ext)s', 'noplaylist': True, 'no_color': True})
        video = None
        try:
            video = ydl.extract_info(url, process=False, download=False)
        except Exception as e:
            print(e)
        return video

    def get_filename(self, youtube_id):
        return "{}.{}".format(youtube_id, self.format_ext)

    def get_opts(self, file_name):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [my_hook],
            'no_color': True,
        }
        return ydl_opts

    def download(self, youtube_id):

        def go():
            update_song = song_file_dao.get_song_file_by_youtube_id(youtube_id)
            file_name = self.get_filename(youtube_id)
            update_song.file_name = file_name
            ydl = youtube_dl.YoutubeDL(self.get_opts(file_name))
            result = ydl.extract_info(youtube_id, process=True, download=True)
            print(result)

        # TODO: This is probably not how to use threads correctly
        t = threading.Thread(target=go)
        t.start()


youtube_id = 'lI2CYUUdwwQ'
d = Downloader.download(self, youtube_id)
