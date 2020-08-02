"""
Author: Adam Wiraszka
Date Started: July 17 2020
"""

import downloader as ad
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
output_directory = 'C:/Users/Adam/Desktop'  # default output directory
root_directory = 'C:/Users/Adam/Desktop/Projects/music/music-downloader'  # Where program files reside
display_text = {'searching': 'Searching for download links...',
                'found': 'Found download links',
                'choosing': 'Choosing best download link',
                'cover': 'Downloading cover art',
                'tags': 'Applying media tags',
                'finishing': 'Finishing up',
                'done': 'Done'}

# use 'clearlooks' for progress bar
# use 'arc' for buttons


class Window(tk.ThemedTk):
    def __init__(self):
        super(Window, self).__init__()
        self.title("Adam's Bomb Ass Music Downloader")
        # print(self.get_themes())
        self.set_theme('arc')  # clearlooks, plastik, arc
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(WIDTH, HEIGHT)
        self.iconphoto(False, PhotoImage(file='my_icon.png'))
        self.create_canvas(15, 5)  # number of rows & columns in grid
        self.create_menu()
        self.create_entry(13, 2)  # row, column
        self.create_search_button(13, 3)  # row, column
        # self.create_button_img()
        self.configure_directories()

    def configure_directories(self):
        self.output_directory = output_directory
        self.root_directory = root_directory

    def create_canvas(self, rows, cols):
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.grid(column=0, row=0, rowspan=rows, columnspan=cols)
        img_main = Image.open('bg_main.jpg')
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
        print(f'shifted text by {shift_pixels} pixels')

    def remove_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

    def switch_page(self, new_page):
        if new_page == 'spotify_page':
            print('spotify page')
            self.spotify_page()
        if new_page == 'download_page':
            print('download page')
            self.download_page()
        if new_page == 'confirmation_page':
            print('confirmation page')
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
                print('valid entry')
            self.center_text('Searching...')
            self.show_text('Searching...', self.x_display, 395)
            self.search_query = self.entry.get()
            self.search_track()

    def search_track(self):
        self.results = ad.spotify_search(self.search_query)
        self.search_status = self.results[1]
        # print(self.search_results)
        print(self.search_status)
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
            'Confirmation', 'Could not find track information.\nDo you wish to download anyways?')
        print('outcome is', self.continue_anyways)
        if self.continue_anyways:
            self.search_str = self.search_query
            self.remove_widgets()
            self.switch_page('download_page')
        else:
            print('cancelled search')

    def spotify_page(self):
        self.create_canvas(15, 7)
        self.create_entry(11, 3)
        self.create_menu()
        self.create_search_button(11, 4)
        self.display_results()

    def dl_albums(self, i):
        print('downloading cover art image')
        ad.dl_cover_art(i, self.search_results)
        cover = Image.open('img.png')  # cover art: 640 x 640
        cover_resized = cover.resize((42, 42), Image.ANTIALIAS)
        print('resized image')
        self.cover_img = ImageTk.PhotoImage(cover_resized)
        self.albums = Label(self.track_frame, image=self.cover_img)
        self.albums.grid(column=2, row=i+3)
        # self.album.lift()

    def dl_results(self):
        pass

    def display_results(self):
        self.buttons = []
        self.details = []
        for i in range(7):  # show top 7 results
            track = self.search_results[i]
            id = track['id']
            artist = track['artist']
            name = track['track']
            album = track['album']
            duration = track['duration']
            display_text = str(id) + ': ' + artist + ' - ' + name + \
                '\n' + 'Album: ' + album + ' - ' + duration
            search_text = artist + ' - ' + name
            self.details.append(search_text)
            self.track_frame = Frame(self)
            self.track_frame.grid(column=2, row=i+3, columnspan=3)
            self.dl_albums(i)
            self.buttons.append(ttk.Button(self.track_frame, text=display_text, width=60,
                                           command=lambda i=i: self.choose_song(i)))
            self.buttons[i].grid(column=3, row=i+3, columnspan=2)

    def choose_song(self, i):
        self.index = i
        print('user choice:', i)
        self.search_str = self.details[i]
        self.remove_widgets()
        self.switch_page('download_page')

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
            print('normal', current)
            self.progress_bar['value'] = i
            self.update_idletasks()
            time.sleep(time_int)
            if self.progress_rush:
                for n in range(current, stop):
                    print('rush', n)
                    self.progress_bar['value'] = n
                    self.update_idletasks()
                    time.sleep(0.03)
                self.progress_rush = False
                break
        self.progress_updating = False

    def progress_control(self):
        # Searching (0-25)
        if self.progress_part == 1:
            print('starting part 1')
            self.update_progress(0, 25, 0.2)  # start %, stop %, time interval between %
        if self.progress_part == 2:
            print('starting part 2')
            self.update_progress(25, 35, 0.08)  # start %, stop %, time interval
        if self.progress_part == 3:
            print('starting part 3')
            self.update_progress(35, 85, 0.3)  # start %, stop %, time interval
        if self.progress_part == 4:
            print('starting part 4')
            self.update_progress(85, 101, 0.05)  # start %, stop %, time interval

    def yt_search(self):
        self.youtube_results = ad.search_youtube(self.search_str)
        print(self.youtube_results)

    def start_search_thread(self):
        self.show_text(display_text['searching'], 305, 395)
        self.progress_part = 1
        self.progress_rush = False
        self.progress_updating = False
        self.progress_thread = threading.Thread(target=self.progress_control).start()
        self.search_thread = threading.Thread(target=self.yt_search)
        self.search_thread.start()
        self.after(100, self.check_search_thread)

    def check_search_thread(self):
        if self.search_thread.is_alive():
            self.after(20, self.check_search_thread)
        else:
            self.progress_rush = True
            print('RUSH TO 25!')
            self.compare_audio()

    def compare_audio(self):
        if self.progress_updating == True:
            print('waiting')
            self.after(80, self.compare_audio)
        elif self.progress_updating == False:
            self.progress_part = 2
            self.center_text(display_text['choosing'])
            self.show_text(display_text['choosing'], self.x_display, 395)
            self.progress_thread = threading.Thread(target=self.progress_control).start()

            if self.search_status == True:
                self.best_choice = ad.match_audio(
                    self.search_str, self.search_results, self.youtube_results, self.index)
                self.output_filename = self.search_str + '.mp3'
                self.after(100, self.start_dl_thread)  # pause so display text can be read
            else:
                self.best_choice = ad.match_string_only(self.search_str, self.youtube_results)
                self.output_filename = self.best_choice[1] + '.mp3'
                self.after(100, self.start_dl_thread)  # pause so display text can be read

    def yt_download(self):
        self.output_name = ad.dl_song(self.best_choice[0], self.output_directory)

    def start_dl_thread(self):
        if self.progress_updating == True:
            print('waiting')
            self.after(80, self.start_dl_thread)
        elif self.progress_updating == False:
            print('STARTING DOWNLOAD')
            self.dl_text = str('Downloading: ' + self.output_filename)
            self.center_text(self.dl_text)
            self.show_text(self.dl_text, self.x_display, 395)
            self.progress_part = 3
            self.progress_thread = threading.Thread(target=self.progress_control).start()
            self.dl_thread = threading.Thread(target=self.yt_download)
            self.dl_thread.start()
            #self.dl_thread.daemon = True
            self.after(100, self.check_dl_thread)

    def check_dl_thread(self):
        if self.dl_thread.is_alive():
            self.after(20, self.check_dl_thread)
        else:
            print('Download complete. RUSH TO 85!')
            self.progress_rush = True
            if self.search_status == True:
                self.dl_cover_art()
            else:
                self.center_text('No track info to add to audio file')
                self.show_text('No track info to add to audio file', self.x_display, 395)
                self.after(500, self.check_media_added)

    def dl_cover_art(self):
        if self.progress_updating == True:
            print('waiting')
            self.after(80, self.dl_cover_art)
        elif self.progress_updating == False:
            self.progress_part = 4
            self.progress_thread = threading.Thread(target=self.progress_control).start()
            self.center_text(display_text['cover'])
            self.show_text(display_text['cover'], self.x_display, 395)
            ad.dl_cover_art(self.index, self.search_results)
            self.after(500, self.apply_media_tags)

    def apply_media_tags(self):
        self.center_text(display_text['tags'])
        self.show_text(display_text['tags'], self.x_display, 395)
        ad.apply_ID3_tags(self.index, self.search_results,
                          self.output_name, self.output_filename, self.root_directory)
        self.after(500, self.check_media_added)

    def check_media_added(self):
        print('Download process complete')
        os.chdir(root_directory)
        self.remove_widgets()
        self.switch_page('confirmation_page')

    def confirmation_page(self):
        #print('cwd is:', os.getcwd())
        self.set_theme('arc')
        self.create_canvas(15, 9)
        self.create_menu()
        # self.create_save_button()
        # self.create_discard_button()
        # self.create_proceed_button()
        self.create_display_frame()
        self.create_test_buttons()

    def create_test_buttons(self):
        self.test_buttons = []
        for i in range(9):
            print('making test buttons')
            self.test_name = 'col ' + str(i) + 'row 14'
            self.test_buttons.append(ttk.Button(self, text=self.test_name,
                                                command=lambda i=i: self.choose_song(i)))
            self.test_buttons[i].grid(column=i, row=14)

    def create_display_frame(self):
        self.display_frame = Frame(self)
        self.display_album = Label(self.display_frame, text='album', bg='red')
        self.display_info1 = Label(self.display_frame, text='track info', bg='blue')
        self.display_info2 = Label(self.display_frame, text='file info', bg='green')

        self.display_frame.grid(row=3, column=3, rowspan=9, columnspan=3)
        self.display_album.grid(row=3, column=3, padx=30, pady=30)
        self.display_info1.grid(row=3, column=4, rowspan=9, columnspan=2, sticky='nsew')
        self.display_info2.grid(row=4, column=3, rowspan=7, columnspan=3, sticky='nsew')

    def create_save_button(self):
        self.search_btn = ttk.Button(self, text='Save Changes',
                                     command=(lambda: self.click_save()))
        self.search_btn.grid(column=3, row=13)

    def create_discard_button(self):
        self.discard_btn = ttk.Button(self, text='Discard Changes',
                                      command=(lambda: self.click_discard()))
        self.discard_btn.grid(column=2, row=13)

    def create_proceed_button(self):
        self.bind('<Return>', (lambda event: self.click_proceed()))
        self.proceed_btn = ttk.Button(self, text='Proceed',
                                      command=(lambda: self.click_proceed()))
        self.proceed_btn.grid(column=4, row=13)

    def click_save(self):
        # self.refresh_window()
        pass

    def click_discard(self):
        # self.refresh_window()
        pass

    def click_proceed(self):
        # self.refresh_window()
        pass


if __name__ == "__main__":
    window = Window()
    window.mainloop()
