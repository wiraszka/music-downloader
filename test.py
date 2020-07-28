import tkinter as tk
from tkinter import font as tkfont
import downloader as ad
import os



class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Set arguments for each frame
        self.frames["StartPage"] = StartPage(parent=container, controller=self)
        self.frames["ResultsPage"] = PageOne(parent=container, controller=self)
        self.frames["FinalPage"] = PageTwo(parent=container, controller=self)

        self.frames["StartPage"].grid(row=0, column=0, sticky="nsew")
        self.frames["ResultsPage"].grid(row=0, column=0, sticky="nsew")
        self.frames["FinalPage"].grid(row=0, column=0, sticky="nsew")


        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Create search/input box
        input = tk.Entry(self, width=50)
        search_query = input.get()
        input.grid(column=0, row=2, sticky='nsew')

        def click_search():
            label = tk.Label(self, text='searching for track...')
            label.grid(column=0, row=0, pady=5)
            search_results = ad.spotify_search(search_query)

            if search_results[1]: # search successful
                self.show_frame("ResultsPage")
            else:
                label = tk.Label(self, text='Search was unsuccessful. Try a different query.')
                label.pack(side="bottom", fill="x", pady=5)
            return search_results

        # Create search button
        search_button = tk.Button(self, text='Search', padx=5, pady=5, fg='white', bg='black',
                                  command=click_search)
        search_button.grid(column=1, row=2, sticky='nsew')



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 1")
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2")
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
