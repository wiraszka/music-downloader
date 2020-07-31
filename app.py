import downloader as ad
import os
import json
import threading
from tkinter import *
from tkinter import ttk
from ttkthemes import themed_tk as tk
from PIL import ImageTk, Image


# Constants
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


class Window(tk.ThemedTk):
    def __init__(self):
        super(Window, self).__init__()
        self.title("Adam's Bomb Ass Music Downloader")
        # print(self.get_themes())
        self.set_theme('clearlooks')
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(WIDTH, HEIGHT)
        self.iconphoto(False, PhotoImage(file='my_icon.png'))
        self.create_canvas()
        self.create_menu()
        self.create_entry()
        self.create_search_button()
        self.configure_directories()

    def configure_directories(self):
        self.output_directory = output_directory
        self.root_directory = root_directory

    def create_canvas(self):
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.grid(column=0, row=0, rowspan=15, columnspan=5)
        img_main = Image.open('bg_main.jpg')
        resized = img_main.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        self.canvas.image = ImageTk.PhotoImage(resized)
        self.canvas.create_image(0, 0, image=self.canvas.image, anchor='nw')

    def create_label(self):
        label_font = ('calibri', 10)
        label = ttk.Label(self, text='Enter a song:', anchor='w')
        label.config(font=label_font)
        label.grid(column=2, row=15)

    def create_entry(self):
        self.input = StringVar()
        self.entry = ttk.Entry(self, textvariable=self.input, width=40)
        self.entry.focus()
        self.entry.grid(column=2, row=13, sticky='ew')

    def create_search_button(self):
        self.bind('<Return>', (lambda event: self.click_search()))
        self.search_btn = Button(self, text='Search', command=(lambda: self.click_search()))
        self.search_btn.grid(column=3, row=13, sticky='w')

    # NOT USED
    def create_button_img(self):
        im = Image.open('search_button_small.png')
        print(im.mode)
        if 'transparency' in im.info:
            print('transparent!')
        self.button_img = PhotoImage(file='search_button_small.png')
        self.button_img_resized = self.button_img.subsample(2, 2)
        self.search_btn = Button(self, image=self.button_img_resized,
                                 command=self.click_search, borderwidth=0)
        self.search_btn.grid(column=3, row=13, sticky='w')

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
            self.invalid_label = Label(self, text='invalid entry.')
            self.invalid_label.grid(column=2, row=14)
        else:
            try:
                self.invalid_label.grid_forget()
            except:
                print('valid entry')
            self.search_query = self.entry.get()
            self.search_btn.configure(text='Searching...')
            self.search_track()

    def search_track(self):
        self.results = ad.spotify_search(self.search_query)
        self.search_results = json.loads(self.results[0])
        self.search_status = self.results[1]
        # print(self.search_results)
        print(self.search_status)
        if self.search_status == True:
            self.remove_widgets()
            self.switch_page('spotify_page')
        else:
            self.search_str = self.search_query
            self.label = Label(self, text='Could not find track.')
            self.label.grid(column=2, row=14)

    def spotify_page(self):
        self.create_canvas()
        self.create_entry()
        self.create_menu()
        self.create_search_button()
        self.display_results()

    def display_results(self):
        self.buttons = []
        self.details = []
        for i in range(7):  # show top 7 results
            track = self.search_results[i]
            # print(track)
            id = track['id']
            artist = track['artist']
            name = track['track']
            album = track['album']
            duration = track['duration']
            display_text = str(id) + ': ' + artist + ' - ' + name + \
                '\n' + 'Album: ' + album + ' - ' + duration
            search_text = artist + ' - ' + name
            self.details.append(search_text)
            self.buttons.append(Button(self, text=display_text, width=50,
                                       command=lambda i=i: self.choose_song(i)))
            self.buttons[i].grid(column=2, row=i+5)

    def choose_song(self, i):
        self.index = i
        print('user choice:', i)
        self.search_str = self.details[i]
        self.remove_widgets()
        self.switch_page('download_page')

    def download_page(self):
        self.create_canvas()
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
            self.update_progress(0, 25, 0.2)  # start %, stop %, time interval
        if self.progress_part == 2:
            print('starting part 2')
            self.update_progress(25, 35, 0.08)  # start %, stop %, time interval
        if self.progress_part == 3:
            print('starting part 3')
            self.update_progress(35, 85, 0.32)  # start %, stop %, time interval
        if self.progress_part == 4:
            print('starting part 4')
            self.update_progress(85, 101, 0.05)  # start %, stop %, time interval

    def show_text(self, alpha_text):
        try:
            self.canvas.delete(self.canvas_text)
        except:
            print('error, could not remove canvas')
        self.canvas_text = self.canvas.create_text(300, 390, text=alpha_text, anchor='nw')

    def yt_search(self):
        self.youtube_results = ad.search_youtube(self.search_str)
        print(self.youtube_results)

    def start_search_thread(self):
        self.show_text(display_text['searching'])
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
            self.show_text(display_text['choosing'])
            self.progress_thread = threading.Thread(target=self.progress_control).start()
            self.best_choice = ad.match_audio(
                self.search_str, self.search_results, self.youtube_results, self.index)
            self.output_filename = str(self.best_choice[1]) + '.mp3'
            self.after(100, self.start_dl_thread)  # pause so display text can be read

    def yt_download(self):
        self.output_name = ad.dl_song(self.best_choice[0], self.output_directory)

    def start_dl_thread(self):
        if self.progress_updating == True:
            print('waiting')
            self.after(80, self.start_dl_thread)
        elif self.progress_updating == False:
            print('STARTING DOWNLOAD')
            self.show_text(str('Downloading: ' + self.output_filename))
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
            self.dl_cover_art()

    def dl_cover_art(self):
        if self.progress_updating == True:
            print('waiting')
            self.after(80, self.dl_cover_art)
        elif self.progress_updating == False:
            self.progress_part = 4
            self.progress_thread = threading.Thread(target=self.progress_control).start()
            self.show_text(display_text['cover'])
            ad.dl_cover_art(self.index, self.search_results)
            self.after(500, self.apply_media_tags)

    def apply_media_tags(self):
        self.show_text(display_text['tags'])
        ad.apply_ID3_tags(self.index, self.search_results,
                          self.output_name, self.output_filename, self.root_directory)
        self.after(500, self.check_media_added)

    def check_media_added(self):
        print('Download process complete')
        self.show_text(display_text['done'])
        self.remove_widgets()
        self.switch_page('confirmation_page')

    def confirmation_page(self):
        print('cwd is:', os.getcwd())
        self.create_canvas()
        self.create_menu()
        self.create_save_button()
        self.create_discard_button()
        self.create_proceed_button()

    def create_save_button(self):
        self.search_btn = Button(self, text='Save Changes',
                                 command=(lambda: self.click_save()))
        self.search_btn.grid(column=3, row=13)

    def create_discard_button(self):
        self.search_btn = Button(self, text='Discard Changes',
                                 command=(lambda: self.click_discard()))
        self.search_btn.grid(column=2, row=13)

    def create_proceed_button(self):
        self.bind('<Return>', (lambda event: self.click_proceed()))
        self.search_btn = Button(self, text='Discard Changes',
                                 command=(lambda: self.click_proceed()))
        self.search_btn.grid(column=4, row=13)

    def click_save(self):
        self.refresh_window()

    def click_discard(self):
        self.refresh_window()

    def click_proceed(self):
        self.refresh_window()


if __name__ == "__main__":
    window = Window()
    window.mainloop()
