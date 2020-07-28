from tkinter import *
from tkinter import ttk
import downloader as se
import time
import os

class App:

    def __init__(self, parent):
        self.widgets(parent)

    def widgets(self, app):
        self.label1 = Label(app, text='Enter a song name:').grid(column=0, row=0, sticky='nsew')
        self.entry = Entry(app, width=50)
        self.entry.grid(column=0, row=1, sticky='nsew')
        self.search_btn = Button(app, text='Search', padx=3, pady=3,
                                    fg='white', bg='black', command=self.click_search)
        self.search_btn.grid(column=1, row=1, sticky='nsew')

        return self


    def 


    def close_window(self):
        self.quit()
        self.destroy()
        exit()

    def create_menu(self):
        menu_bar = Menu(self)
        self.config(menu = menu_bar)

        file_menu = Menu(menu_bar, tearoff = 0)
        menu_bar.add_cascade(label = 'File', menu = file_menu)
        file_menu.add_command(label = 'Refresh', command = self.refresh_window)
        file_menu.add_command(label = 'Settings')
        file_menu.add_command(label = 'Exit', command = self.close_window)

        help_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label = 'Help', menu = help_menu)
        help_menu.add_command(label = 'About')

    def change_frame(self, search_results, status):
        print('yay')
        pass

    def click_search(self):
        # Display SEARCHING text
        self.label = Label(root, text='searching for track...')
        self.label.grid(column=0, row=2, pady=5)
        # Fetch entry string
        self.search_query = self.entry.get()
        # Search Spotify
        search_results = se.spotify_search(self.search_query)
        if search_results[1]:
            status = 'search successful'
        else:
            status = 'search unsuccessful'
            self.status_label = Label(root, text=status)
            self.status_label.grid(column=0, row=3, pady=5)
        return self, search_results, status




root = Tk()
obj = App(root)
root.mainloop()
