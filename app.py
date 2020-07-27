import downloader as se
import os
from tkinter import *

HEIGHT = 250
WIDTH = 400

def main():
    root = Tk()
    window = App(root)
    return None

class App:
    # Constructor
    def __init__(self, root):
        #self.canvas = Canvas(root, height=HEIGHT, width=WIDTH, bg='#263D42')
        #self.canvas.grid(row=0, sticky='nsew')
        self.input = Entry(root, width=50).grid(column=0, row=1, sticky='nsew')
        self.search_button = Button(root, text='Search', padx=5, pady=5,
                                    fg='white', bg='black', command=self.click_search)
        self.search_button.grid(column=1, row=1, sticky='nsew')
        self.root.mainloop()

    # Execute spotify search
    def click_search(self):
        search_query = self.input.get()
        search_results = se.spotify_search(self.search_query)
        if search_results[1]:
            status_text = 'search successful'
        else:
            status_text = 'search unsuccessful'
        label = tk.Label(root, text=status_text)
        label.grid(column=0, row=1)
        return None


main()
# # Run application
# if __name__ == "__main__":
#     main()
