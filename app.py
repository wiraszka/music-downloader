"""
Author: Adam Wiraszka
Date Started: July 17 2020
"""

# Import local scripts
import search_spotify as sp
import search_youtube as yt
import downloader as ad
import process_text as pt

# Import dependencies
import os
import json
import time
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import themed_tk as tk
from PIL import ImageTk, Image


# CONSTANTS
HEIGHT = 432
WIDTH = 768
output_directory = 'C:/Users/Adam/Desktop/songs'  # audio file destination
root_directory = 'C:/Users/Adam/Desktop/Projects/music/music-downloader'  # program files location
cover_art_directory = 'C:/Users/Adam/Desktop/Projects/music/music-downloader/images/cover_art' # cover art dl destination


class Window(tk.ThemedTk):
    def __init__(self):
        super(Window, self).__init__()
        print('='*80)
        print('PROCESS SUMMARY')
        print('='*80)
        self.title("Adam's Bomb Ass Music Downloader")
        self.set_theme('arc')  # clearlooks, plastik, arc
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(WIDTH, HEIGHT)
        self.iconphoto(False, PhotoImage(file='images/my_icon.png'))
        self.create_canvas(15, 5)  # number of rows & columns in grid
        self.create_menu()
        self.create_entry(13, 2)  # row, column
        self.create_search_button(13, 3)  # row, column
        self.configure_directories()

    def configure_directories(self):
        self.output_directory = output_directory
        self.root_directory = root_directory
        self.cover_art_directory = cover_art_directory

    def create_canvas(self, rows, cols):
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.grid(column=0, row=0, rowspan=rows, columnspan=cols)
        img_main = Image.open('images/bg_main.jpg')
        resized = img_main.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        self.canvas.image = ImageTk.PhotoImage(resized)
        self.canvas.create_image(0, 0, image=self.canvas.image, anchor='nw')

    def create_label(self):
        label_font = ('calibri', 10)
        label = ttk.Label(self, text='Enter a song:', anchor='w')
        label.config(font=label_font)
        label.grid(column=2, row=15)

    def create_entry(self, row, col):
        self.input = StringVar()
        self.entry = ttk.Entry(self, textvariable=self.input, width=40)
        self.entry.focus()
        self.entry.grid(column=col, row=row, sticky='ew')  # 2, 13

    def create_search_button(self, row, col):
        self.bind('<Return>', (lambda event: self.click_search()))
        self.search_btn = ttk.Button(self, text='Search', command=(lambda: self.click_search()))
        self.search_btn.grid(column=col, row=row, sticky='w')  # 3, 13

    def create_menu(self):
        menu_bar = Menu(self)
        self.config(menu=menu_bar)
        # Create FILE menu bar
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Refresh', command=self.refresh_window)
        file_menu.add_command(label='Settings')
        file_menu.add_command(label='Exit', command=self.close_window)
        # Create HELP menu bar
        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='About')

    def create_progressbar(self):
        self.progress_bar = ttk.Progressbar(self, orient='horizontal',
                                            length=250, mode='indeterminate')
        self.progress_bar.grid(column=2, row=13, pady=10)
        self.progress_bar['value'] = 0

    def show_text(self, alpha_text, xpixel, ypixel):
        try:
            self.canvas.delete(self.canvas_text)
        except:
            pass
        self.canvas_text = self.canvas.create_text(xpixel, ypixel, text=alpha_text, anchor='nw')

    def center_text(self, text):
        char_count = len(text)
        pixel_count = char_count * 5.8  # pixels per character
        shift_pixels = pixel_count / 2
        self.x_display = 384 - shift_pixels
        #print(f'shifted text by {shift_pixels} pixels')

    def resize_cover_art(self, width, height, file):
        cover = Image.open(file)  # cover art dimensions: 640 x 640
        cover_resized = cover.resize((width, height), Image.ANTIALIAS)  # resize to 42 x 42
        #print('resized image to:', width, 'x', height)
        cover_img = ImageTk.PhotoImage(cover_resized)
        return cover_img

    def remove_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

    def switch_page(self, new_page):
        if new_page == 'spotify_page':
            self.spotify_page()
        if new_page == 'download_page':
            self.download_page()
        if new_page == 'confirmation_page':
            self.confirmation_page()

    def refresh_window(self):
        self.destroy()
        self.__init__()

    def close_window(self):
        self.quit()
        self.destroy()
        exit()

    def click_search(self):
        if self.entry.get() == '':
            self.show_text('Invalid Entry', 346, 394)
        else:
            try:
                self.canvas.delete(self.canvas_text)
            except:
                print('Valid entry by user.')
            self.center_text('Searching...')
            self.show_text('Searching...', self.x_display, 395)
            self.search_query = self.entry.get()
            self.search_track()

    def search_track(self):
        self.results = sp.spotify_search(self.search_query)
        self.search_status = self.results[1]
        if self.search_status == True:
            self.search_results = json.loads(self.results[0])
            self.remove_widgets()
            self.switch_page('spotify_page')
        else:
            self.search_failed()

    def search_failed(self):
        self.center_text('Could not find track')
        self.show_text('Could not find track', self.x_display, 395)
        self.continue_anyways = messagebox.askokcancel(
            'Confirmation', 'Could not find track information.\nDownload audio anyways?')
        print('Outcome is:', self.continue_anyways)
        if self.continue_anyways:
            self.search_str = self.search_query
            self.remove_widgets()
            self.switch_page('download_page')
        else:
            print('Cancelled search.')

# =======  SEARCH SPOTIFY  ==================================================================================================

    def spotify_page(self):
        self.create_canvas(15, 7)
        self.create_menu()
        self.start_sp_threads()

    def start_sp_threads(self):
        self.sp_status = True
        # Start main thread to download cover art images
        self.dl_albums_thread = threading.Thread(target=self.sp_albums)
        self.dl_albums_thread.start()
        # Start thread to display 'Searching' animation
        self.search_animation_thread = threading.Thread(
            target=self.searching_animation, args=['Searching'])
        self.search_animation_thread.start()

        self.after(100, self.check_sp_albums)

    def searching_animation(self, text):
        self.x_display = 349
        while self.sp_status == True:
            self.text = text
            time.sleep(0.3)
            self.text = text + '.'
            time.sleep(0.3)
            self.text = text + '..'
            time.sleep(0.3)
            self.text = text + '...'
            time.sleep(0.3)

    def sp_albums(self):
        for i in range(len(self.search_results)):
            ad.dl_cover_art(i, self.search_results, self.cover_art_directory, self.root_directory)

    def check_sp_albums(self):
        if self.dl_albums_thread.is_alive():
            self.show_text(self.text, self.x_display, 395)
            self.after(300, self.check_sp_albums)
        else:
            self.sp_status = False
            print('Successfully downloaded cover art images.')
            self.canvas.delete(self.canvas_text)
            self.sp_results_page()

# =======  SHOW SPOTIFY RESULTS  ==============================================================================================

    def sp_results_page(self):
        self.get_sp_results()
        self.show_sp_results()
        self.create_search_button(11, 4)
        self.create_entry(11, 3)

    def get_sp_results(self):
        self.search_details = []
        self.search_info = []
        for i in range(len(self.search_results)):  # show top 7 results
            track = self.search_results[i]
            search_text = track['artist'] + ' - ' + track['track']
            display_text = str(track['id']) + ': ' + track['artist'] + ' - ' + track['track'] + \
                '\n' + 'Album: ' + track['album'] + ' - ' + track['duration']
            display_text_centered = pt.modify_text(display_text)
            self.search_details.append(search_text)
            self.search_info.append(display_text_centered)

    def show_sp_results(self):
        self.buttons = []
        self.albums = []
        for i in range(len(self.search_results)):
            self.spotify_frame = Frame(self)
            self.spotify_frame.grid(column=2, row=i+3, columnspan=3)
            self.buttons.append(ttk.Button(self.spotify_frame, text=self.search_info[i], width=60,
                                           command=lambda i=i: self.choose_song(i)))
            self.buttons[i].grid(column=3, row=i+3, columnspan=2)
            img = f'img{i}.png'  # cover art dimensions: 640 x 640
            img_file = cover_art_directory + '/' + img
            cover_resized = self.resize_cover_art(42, 42, img_file)  # resize to 42 x 42
            self.album_label = Label(self.spotify_frame)  # create label
            self.album_label.image = cover_resized  # anchor image
            self.album_label.configure(image=cover_resized)  # set image on label
            self.albums.append(self.album_label)
            self.albums[i].grid(column=2, row=i+3)

    def choose_song(self, i):
        self.index = i
        print('User song choice:', i + 1)
        self.search_str = self.search_details[i]
        self.remove_widgets()
        self.switch_page('download_page')

# =======  DOWNLOAD AUDIO FILE  ============================================================================================

    def download_page(self):
        self.set_theme('clearlooks')
        self.create_canvas(15, 5)
        self.create_menu()
        self.create_progressbar()
        self.start_search_thread()

    def update_progress(self, start, stop, time_int):
        self.progress_updating = True
        for i in range(start, stop):
            current = i
            #print('progress:', current)
            self.progress_value = i
            time.sleep(time_int)
            if self.progress_rush:
                for n in range(current, stop):
                    #print('rush:', n)
                    self.progress_value = n
                    time.sleep(0.03)
                self.progress_rush = False
                break
        self.progress_updating = False

    def progress_control(self):
        '''
        Controls progress bar progression.
            Part 1: Connecting to Youtube API and searching Youtube (0%-25%)
            Part 2: Analyzing Youtube results and finding best match (25%-35%)
            Part 3: Downloading audio from Youtube (35%-85%)
            Part 4: Adding media tags and cover art to audio file (85%-100%)
        '''
        if self.progress_part == 1:
            self.update_progress(0, 25, 0.2)  # start %, stop %, time interval between %
        if self.progress_part == 2:
            self.update_progress(25, 35, 0.08)  # start %, stop %, time interval
        if self.progress_part == 3:
            self.update_progress(35, 85, 0.3)  # start %, stop %, time interval
        if self.progress_part == 4:
            self.update_progress(85, 101, 0.05)  # start %, stop %, time interval

    def update_progress_gui(self):
        self.progress_bar['value'] = self.progress_value

    def establish_connect_anim(self):
        if self.progress_part == 1:
            self.progress_updating = False
            print('Establishing Connection!')
            self.canvas.delete(self.canvas_text)
            self.sp_status = True
            self.connecting_annimation = threading.Thread(
                target=self.searching_animation, args=['Establishing Connection'])
            self.connecting_annimation.start()

    def yt_search(self):
        self.youtube_results = yt.search_yt(self.search_str)

    def start_search_thread(self):
        self.show_text('Searching for download links...', 305, 395)
        self.progress_part = 1
        self.progress_rush = False
        self.progress_updating = False
        self.progress_thread = threading.Thread(target=self.progress_control)
        self.progress_thread.start()
        self.search_thread = threading.Thread(target=self.yt_search)
        self.search_thread.daemon = True
        self.search_thread.start()

        self.after(100, self.check_search_thread)

    def check_search_thread(self):
        if self.search_thread.is_alive():
            self.update_progress_gui()
            self.after(80, self.check_search_thread)
        else:
            self.progress_rush = True
            #print('RUSH TO 25!')
            self.compare_audio()

    def compare_audio(self):
        if self.progress_updating == True:
            #print('waiting')
            self.update_progress_gui()
            self.after(80, self.compare_audio)
        elif self.progress_updating == False:
            self.sp_status = False
            self.progress_part = 2
            self.center_text('Choosing best download link')
            self.show_text('Choosing best download link', self.x_display, 395)
            self.progress_thread = threading.Thread(target=self.progress_control).start()
            # Conditional True if spotify search was successful
            if self.search_status == True:
                self.best_choice = yt.match_audio(
                    self.search_str, self.search_results, self.youtube_results, self.index)
                self.output_filename = self.search_str + '.mp3'
                self.after(100, self.start_dl_thread)  # pause so display text can be read
            # Conditional False if spotify search unsuccessful
            else:
                self.best_choice = yt.match_string_only(self.search_str, self.youtube_results)
                self.output_filename = self.best_choice[1] + '.mp3'
                self.after(100, self.start_dl_thread)  # pause so display text can be read

    def yt_download(self):
        self.output_filename = ad.dl_song(self.best_choice[0], self.output_directory)

    def start_dl_thread(self):
        if self.progress_updating == True:
            #print('waiting')
            self.update_progress_gui()
            self.after(80, self.start_dl_thread)
        elif self.progress_updating == False:
            print('STARTING DOWNLOAD.')
            self.dl_text = str('Downloading: ' + self.output_filename)
            self.center_text(self.dl_text)
            self.show_text(self.dl_text, self.x_display, 395)
            self.progress_part = 3
            self.progress_thread = threading.Thread(target=self.progress_control).start()
            self.dl_thread = threading.Thread(target=self.yt_download)
            self.dl_thread.daemon = True
            self.dl_thread.start()
            self.after(100, self.check_dl_thread)

    def check_dl_thread(self):
        if self.dl_thread.is_alive():
            self.update_progress_gui()
            self.after(20, self.check_dl_thread)
        else:
            self.progress_rush = True
            if self.progress_updating == True:
                self.update_progress_gui()
                self.after(20, self.check_dl_thread)
            else:
                self.start_media_thread()

    def start_media_thread(self):
        print('Download completed successfully.')
        if self.search_status == True:
            self.progress_part = 4
            self.progress_thread = threading.Thread(target=self.progress_control).start()
            self.center_text('Fetching cover art')
            self.show_text('Fetching cover art', self.x_display, 395)
            self.after(100, self.apply_media_tags)
        else:
            self.center_text('No track info to add to audio file')
            self.show_text('No track info to add to audio file', self.x_display, 395)
            self.after(500, self.switch_to_confirmation)


    def apply_media_tags(self):
        self.center_text('Applying media tags')
        self.show_text('Applying media tags', self.x_display, 395)
        self.downloading = True
        ad.apply_ID3_tags(self.index, self.search_results,
                          self.output_filename, self.root_directory, self.downloading, self.output_directory, self.cover_art_directory)
        self.after(500, self.check_media_added)

    def check_media_added(self):
        if self.progress_updating == True:
            self.update_progress_gui()
            self.after(60, self.check_media_added)
        else:
            print('Media tags and album art applied to audio file.')
            self.switch_to_confirmation()

    def switch_to_confirmation(self):
        os.chdir(root_directory)
        self.remove_widgets()
        self.switch_page('confirmation_page')

# =======  CONFIRM SONG DETAILS  ============================================================================================

    def confirmation_page(self):
        #print('cwd is:', os.getcwd())
        self.set_theme('arc')
        self.create_canvas(15, 9)
        self.create_menu()
        self.create_display_frame()
        self.display_album_cover()
        self.display_file_info()
        self.display_song_info()
        self.create_save_button()
        self.create_discard_button()
        self.create_proceed_button()
        # self.create_test_buttons()

    def create_display_frame(self):
        # Create new frame
        self.display_frame = Frame(self, height=350, width=480)  # 320
        self.display_frame.grid(row=2, column=0, rowspan=13, columnspan=12)
        # self.display_title = Label(self.display_frame, text='Please confirm track information')

    def display_album_cover(self):
        # Create label displaying COVER ART
        self.display_album = Label(self.display_frame, bd=5, bg='ivory2', anchor='w')
        img = f'img{self.index}.png'  # cover art dimensions: 640 x 640
        img_file = self.cover_art_directory + '/' + img
        cover_resized = self.resize_cover_art(190, 190, img_file)  # resize to 190 x 190
        self.display_album.image = cover_resized  # anchor image
        self.display_album.configure(image=cover_resized)  # set image on label
        self.display_album.grid(row=0, column=0, rowspan=8, columnspan=8)

    def display_file_info(self):
        # Create and set labels for DURATION and BITRATE
        self.display_duration = Label(self.display_frame, text=(
            'Duration: ' + str(self.search_results[self.index]['duration'])))
        self.display_bitrate = Label(self.display_frame, text='Bitrate: 320kbps')
        self.display_duration.grid(row=8, column=0, columnspan=6)
        self.display_bitrate.grid(row=9, column=0, columnspan=6)

    def display_song_info(self):
        # Artist Name
        self.display_artist = Label(self.display_frame, text='Artist:', width=40)
        self.display_artist.grid(row=0, column=8, columnspan=5)
        self.entry_artist = ttk.Entry(self.display_frame, width=43)
        self.entry_artist.insert(0, self.search_results[self.index]['artist'])
        self.entry_artist.grid(row=1, column=8, columnspan=5)

        # Song Name
        self.display_track = Label(self.display_frame, text='Song:', width=40)
        self.display_track.grid(row=2, column=8, columnspan=5)
        self.entry_track = ttk.Entry(self.display_frame, width=43)
        self.entry_track.insert(0, self.search_results[self.index]['track'])
        self.entry_track.grid(row=3, column=8, columnspan=5)

        # Genre
        self.display_genre = Label(self.display_frame, text='Genre:', width=40)
        self.display_genre.grid(row=4, column=8, columnspan=5)
        self.entry_genre = ttk.Entry(self.display_frame, width=43)
        self.entry_genre.grid(row=5, column=8, columnspan=5)

        # Album Name
        self.display_album_name = Label(self.display_frame, text='Album:', width=40)
        self.display_album_name.grid(row=6, column=8, columnspan=5)
        self.entry_album_name = ttk.Entry(self.display_frame, width=43)
        self.entry_album_name.insert(0, self.search_results[self.index]['album'])
        self.entry_album_name.grid(row=7, column=8, columnspan=5)

        # Release Year
        self.display_year = Label(self.display_frame, text='Year:', anchor='w')
        self.display_year.grid(row=8, column=8, columnspan=2)
        self.entry_year = ttk.Entry(self.display_frame, width=5)
        self.entry_year.insert(0, self.search_results[self.index]['year'])
        self.entry_year.grid(row=9, column=8, columnspan=2)

        # Track Number
        self.display_track_num = Label(self.display_frame, text='Track #:')
        self.display_track_num.grid(row=8, column=10, columnspan=1)
        self.entry_track_num = ttk.Entry(self.display_frame, width=3)
        self.entry_track_num.insert(0, self.search_results[self.index]['track_number'])
        self.entry_track_num.grid(row=9, column=10, columnspan=1)

        # Total Tracks
        self.display_total_tracks = Label(self.display_frame, text='Total Tracks:')
        self.display_total_tracks.grid(row=8, column=11, columnspan=1)
        self.entry_total_tracks = ttk.Entry(self.display_frame, width=3)
        self.entry_total_tracks.insert(0, self.search_results[self.index]['total_tracks'])
        self.entry_total_tracks.grid(row=9, column=11, columnspan=1)

    def create_test_buttons(self):
        self.test_buttons = []
        for i in range(9):
            print('making test buttons')
            self.test_name = 'col ' + str(i) + 'row 14'
            self.test_buttons.append(ttk.Button(self, text=self.test_name,
                                                command=lambda i=i: self.choose_song(i)))
            self.test_buttons[i].grid(column=i, row=14)

    def create_save_button(self):
        self.search_btn = ttk.Button(self.display_frame, text='Save Changes',
                                     command=(lambda: self.click_save()))
        self.search_btn.grid(column=0, row=11, columnspan=4, sticky='nsew')

    def create_discard_button(self):
        self.discard_btn = ttk.Button(self.display_frame, text='Discard Changes',
                                      command=(lambda: self.click_discard()))
        self.discard_btn.grid(column=4, row=11, columnspan=4, sticky='nsew')

    def create_proceed_button(self):
        self.bind('<Return>', (lambda event: self.click_proceed()))
        self.proceed_btn = ttk.Button(self.display_frame, text='Proceed',
                                      command=(lambda: self.click_proceed()))
        self.proceed_btn.grid(column=8, row=11, columnspan=5, sticky='nsew')

    def click_save(self):
        # self.refresh_window()
        pass

    def click_discard(self):
        self.refresh_window()

    def click_proceed(self):
        self.downloading = False
        self.search_results[self.index]['artist'] = self.entry_artist.get()
        self.search_results[self.index]['track'] = self.entry_track.get()
        self.search_results[self.index]['album'] = self.entry_album_name.get()
        self.search_results[self.index]['track_number'] = self.entry_track_num.get()
        #self.search_results[self.index]['total_tracks'] = self.entry_total_tracks.get()
        self.search_results[self.index]['year'] = self.entry_year.get()
        self.search_results[self.index]['genre'] = self.entry_genre.get()
        ad.apply_ID3_tags(self.index, self.search_results,
                          self.output_filename, self.root_directory, self.downloading, self.output_directory, self.cover_art_directory)
        self.remove_widgets()
        self.refresh_window()


if __name__ == "__main__":
    window = Window()
    window.mainloop()
