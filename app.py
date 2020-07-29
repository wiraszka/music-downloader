import downloader as ad
import time
import os
import json
import threading
from tkinter import *
from tkinter import ttk
from ttkthemes import themed_tk as tk
from PIL import ImageTk, Image


HEIGHT = 432
WIDTH = 768

display_text = {'searching': 'Searching for download links...',
                'found': 'Found download links',
                'choosing': 'Choosing best download link',
                'tags': 'Applying media tags and cover art',
                'finishing': 'Finishing up',
                'done': 'Done'}

class Window(tk.ThemedTk):
    def __init__(self):
        super(Window, self).__init__()
        self.title("Adam's Bomb Ass Music Downloader")
        #print(self.get_themes())
        self.set_theme('clearlooks')
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(WIDTH, HEIGHT)
        self.iconphoto(False, PhotoImage(file='my_icon.png'))
        self.create_canvas()
        self.create_entry()
        self.create_button()
        #self.create_button_img()
        self.create_menu()


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
        label.config(font = label_font)
        label.grid(column=2, row=15)


    def create_entry(self):
        self.input = StringVar()
        self.entry = ttk.Entry(self, textvariable=self.input, width=40)
        self.entry.focus()
        self.entry.grid(column=2, row=13, sticky='ew')


    def create_button(self):
        self.search_btn = Button(self, text='Search', command=self.click_search)
        self.search_btn.grid(column=3, row=13, sticky='w')

    # NOT USED
    def create_button_img(self):
        im = Image.open('search_button_small.png')
        print(im.mode)
        if 'transparency' in im.info:
            print('transparent!')
        self.button_img = PhotoImage(file='search_button_small.png')
        self.button_img_resized = self.button_img.subsample(2, 2)
        self.search_btn = Button(self, image=self.button_img_resized, command=self.click_search, borderwidth=0)
        self.search_btn.grid(column=3, row=13, sticky='w')


    def create_menu(self):
        menu_bar = Menu(self)
        self.config(menu = menu_bar)
        # Create FILE menu bar
        file_menu = Menu(menu_bar, tearoff = 0)
        menu_bar.add_cascade(label = 'File', menu = file_menu)
        file_menu.add_command(label = 'Refresh', command = self.refresh_window)
        file_menu.add_command(label = 'Settings')
        file_menu.add_command(label = 'Exit', command = self.close_window)
        # Create HELP menu bar
        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label = 'Help', menu = help_menu)
        help_menu.add_command(label = 'About')


    def create_progressbar(self):
        self.progress_bar = ttk.Progressbar(self, orient = 'horizontal',
                                            length = 250, mode = 'indeterminate')
        self.progress_bar.grid(column=2, row=13, pady=10)
        self.progress_bar['value'] = 0


    def remove_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()


    def switch_page(self):
        if self.new_page == 'spotify_page':
            print('spotify page')
            self.spotify_page()
        if self.new_page == 'download_page':
            print('download page')
            self.download_page()


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
            self.search_btn.configure(text = 'Searching...')
            self.search_track()


    def search_track(self):
        self.results = ad.spotify_search(self.search_query)
        self.search_results = json.loads(self.results[0])
        self.search_status = self.results[1]
        #print(self.search_results)
        print(self.search_status)
        if self.search_status:
            self.new_page = 'spotify_page'
            self.remove_widgets()
            self.switch_page()
        else:
            self.label = Label(self, text='Could not find track.')
            self.label.grid(column=2, row=14)


    def spotify_page(self):
        self.create_canvas()
        self.create_entry()
        self.create_menu()
        self.create_button()
        self.display_results()


    def display_results(self):
        self.buttons = []
        self.details = []
        i = -1
        for track in self.search_results:
            i += 1
            #print(track)
            id = track['id']
            artist = track['artist']
            name = track['track']
            album = track['album']
            duration = track['duration']
            display_text = str(id) + ': ' + artist + ' - ' + name + ' - ' + duration
            search_text = artist + ' - ' + name
            self.details.append(search_text)
            self.buttons.append(Button(self, text=display_text, width=40,
                                       command = lambda i=i: self.choose_song(i)))
            self.buttons[i].grid(column=3, row=i+3, sticky='w')


    def choose_song(self, i):
        self.index = i
        print('user choice:', i)
        self.search_str = self.details[i]
        self.new_page = 'download_page'
        self.remove_widgets()
        self.switch_page()


    def download_page(self):
        self.create_canvas()
        self.create_menu()
        self.create_progressbar()
        self.start_search_thread()


    def start_search_thread(self):
        self.show_text(display_text['searching'])
        self.progress_part = 1
        self.progress_rush = False
        self.progress_updating = False
        self.progress_thread = threading.Thread(target=self.progress).start()
        self.search_thread = threading.Thread(target=self.yt_search)
        self.search_thread.daemon = True
        self.search_thread.start()
        self.after(20, self.check_search_thread)


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
            self.progress_thread = threading.Thread(target=self.progress).start()
            self.best_choice = ad.match_audio(self.search_str, self.search_results, self.youtube_results, self.index)
            self.output_filename = str(self.best_choice[1])
            self.after(900, self.start_dl_thread)  # pause so display text can be read


    def start_dl_thread(self):
        if self.progress_updating == True:
            print('waiting')
            self.after(80, self.start_dl_thread)
        elif self.progress_updating == False:
            dl_text = 'Downloading: ' + self.output_filename
            self.show_text(dl_text)
            self.progress_part = 3
            self.progress_thread = threading.Thread(target=self.progress).start()
            self.dl_thread = threading.Thread(target=self.yt_download)
            self.dl_thread.daemon = True
            self.dl_thread.start()
            self.after(20, self.check_dl_thread)


    def check_dl_thread(self):
        if self.dl_thread.is_alive():
            self.after(20, self.check_dl_thread)
        else:
            print('RUSH TO 85!')
            self.progress_rush = True
            self.apply_media_tags()


    def apply_media_tags(self):
        if self.progress_updating == True:
            print('waiting')
            self.after(80, self.apply_media_tags)
        elif self.progress_updating == False:
            self.progress_part = 4
            self.progress_thread = threading.Thread(target=self.progress).start()
            self.show_text(display_text['tags'])
            ad.dl_cover_art(self.index, self.search_results)
            ad.apply_ID3_tags(self.index, self.search_results, self.output_name, self.output_filename)
            self.after(20, self.check_dl_complete)


    def check_dl_complete(self):
        if self.progress_thread.is_alive():
            self.after(20, self.check_dl_thread)
        else:
            print('Download process complete')
            self.show_text(display_text['done'])
            self.final()


    def final(self):
        print('YAY')


    def progress(self):
        # Searching (0-25)
        if self.progress_part == 1:
            self.progress_updating = True
            print('starting part 1')
            for i in range(25):
                current = i
                print(current)
                self.progress_bar['value'] = i
                self.update_idletasks()
                time.sleep(0.2)
                if self.progress_rush:
                    for n in range(current, 25):
                        print(n)
                        self.progress_bar['value'] = n
                        self.update_idletasks()
                        time.sleep(0.03)
                    self.progress_rush = False
                    break
            self.progress_updating = False
        # Choosing (25-35)
        if self.progress_part == 2:
            self.progress_updating = True
            print('starting part 2')
            for i in range(25,35):
                print(i)
                self.progress_bar['value'] = i
                self.update_idletasks()
                time.sleep(0.08)
            self.progress_updating = False
        # Downloading (35-85)
        if self.progress_part == 3:
            self.progress_updating = True
            print('starting part 3')
            for i in range(35,85):
                current = i
                print(current)
                self.progress_bar['value'] = i
                self.update_idletasks()
                time.sleep(0.35)
                if self.progress_rush:
                    for n in range(current, 85):
                        print(n)
                        self.progress_bar['value'] = n
                        self.update_idletasks()
                        time.sleep(0.04)
                    self.progress_rush = False
                    break
            self.progress_updating = False
        # Applying media (85-100)
        if self.progress_part == 4:
            self.progress_updating = True
            print('starting part 4')
            for i in range(85,101):
                print(i)
                self.progress_bar['value'] = i
                self.update_idletasks()
                time.sleep(0.05)
            self.progress_updating = False


    def yt_search(self):
        self.youtube_results = ad.search_youtube(self.search_str)
        print(self.youtube_results)


    def yt_download(self):
        self.output_name = ad.dl_song(self.best_choice[0])
        self.show_text(display_text['tags'])


    def show_text(self, alpha_text):
        try:
            self.canvas.delete(self.canvas_text)
        except:
            pass
        self.canvas_text = self.canvas.create_text(300,390, text = alpha_text, anchor='nw')




class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder='Enter song name', color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()



if __name__ == "__main__":
    window = Window()
    window.mainloop()
