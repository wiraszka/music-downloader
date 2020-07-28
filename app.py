import downloader as ad
import os
import json
from tkinter import *
from tkinter import ttk
from ttkthemes import themed_tk as tk
from PIL import ImageTk, Image


HEIGHT = 432
WIDTH = 768

# def main():
#     root = Tk()
#     window = App(root)
#     return None

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
        #self.create_label()
        self.create_entry()
        self.create_button()
        #self.create_button_img()
        self.create_menu()


    def create_canvas(self):
        canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        canvas.grid(column=0, row=0, rowspan=15, columnspan=5)
        img_main = Image.open('bg_main.jpg')
        resized = img_main.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        canvas.image = ImageTk.PhotoImage(resized)
        canvas.create_image(0, 0, image=canvas.image, anchor='nw')


    def create_label(self):
        label_font = ('calibri', 10)
        label = ttk.Label(self, text='Enter a song:', anchor='w')
        label.config(font = label_font)
        label.grid(column=0, row=12)


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
            self.display_results()
        else:
            self.label = Label(self, text='Could not find track.')
            self.label.grid(column=2, row=14)

    # NOT USED
    def remove_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

    # NOT USED
    def switch_frame(self):
        if self.new_page == 'spotify_page':
            print('spotify page')
            self.create_spotify_page()
        elif self.new_page == 'download_page':
            print('download page')


    def display_results(self):
        for track in self.search_results:
            #print(track)
            id = track['id']
            artist = track['artist']
            name = track['track']
            album = track['album']
            duration = track['duration']
            display_text = str(id) + ':' + artist + ' - ' + name + ' - ' + duration
            button_info = Button(self, text=display_text, width=40)
            button_info.grid(column=2)
            print(display_text)


    def create_progressbar(self):
        self.progress_bar = ttk.Progressbar(self, orient = 'horizontal',
                                            length = 180, mode = 'determinate')
        self.progress_bar.grid(column=0, row=3, pady=10)





class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
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




window = Window()
window.mainloop()




# # Run application
# if __name__ == "__main__":
#main()
