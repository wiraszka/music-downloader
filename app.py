import downloader as ad
import os
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image


HEIGHT = 320
WIDTH = 480

# def main():
#     root = Tk()
#     window = App(root)
#     return None

class Window(Tk):
    def __init__(self):
        super(Window, self).__init__()

        self.title("Adam's Bomb Ass Music Downloader")
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(WIDTH, HEIGHT)
        self.iconphoto(False, PhotoImage(file='my_icon.png'))
        self.create_canvas()
        #self.create_label()
        self.create_entry()
        self.create_button()
        self.create_menu()


    def create_canvas(self):
        canvas = Canvas(self, height=HEIGHT, width=WIDTH)
        coord = 10, 50, 280, 210
        canvas.grid(column=0, row=0, rowspan=15, columnspan=5)
        img_main = Image.open('bg_main_480x320.jpg')
        canvas.image = ImageTk.PhotoImage(img_main)
        canvas.create_image(0, 0, image=canvas.image, anchor='nw')


    def create_label(self):
        label_font = ('calibri', 10)
        label = Label(self, text='Enter a song:', anchor='w')
        label.config(font = label_font)
        label.grid(column=0, row=12)


    def create_entry(self):
        self.input = StringVar()
        self.entry = Entry(self, textvariable=self.input, width=40)
        self.entry.focus()
        self.entry.grid(column=2, row=13, sticky='ew')


    def create_button(self):
        self.search_btn = Button(self, text='Search', padx=1, pady=1,
                                 fg='white', bg='black', command=self.click_search)
        self.search_btn.grid(column=3, row=13, sticky='ew')


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
        self.search_results = self.results[0]
        self.search_status = self.results[1]
        print(self.search_results)
        print(self.search_status)
        if self.search_status:
            self.new_page = 'spotify_page'
            self.switch_frame()        
        else:
            self.label = Label(self, text='Could not find track.')
            self.label.grid(column=2, row=14)

    def switch_frame(self):
        self.entry.grid_forget()
        self.search_btn.grid_forget()
        if self.new_page == 'spotify_page':
            print('new page')










    def create_progressbar(self):
        self.progress_bar = ttk.Progressbar(self, orient = 'horizontal',
                                            length = 180, mode = 'determinate')
        self.progress_bar.grid(column=0, row=3, pady=10)





window = Window()
window.mainloop()




# # Run application
# if __name__ == "__main__":
#main()
