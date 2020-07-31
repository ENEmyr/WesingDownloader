import tkinter as tk
import threading
from os import mkdir
from os.path import join, abspath, exists
from wesing_downloader import download_albums, download_tracks

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', width=10):
        super().__init__(master, width=width)

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

window = tk.Tk()

title = tk.Label(master=window, text='WeSing Downloader Version 0.1.0 Alpha')
title.grid(row=0)
tracks_txt = tk.Label(master=window, text='Download Tracks')
tracks_txt.grid(row=1)
track_uid = EntryWithPlaceholder(master=window, placeholder="User ID", width=60)
track_uid.grid(row=1, column=1)
number_tracks = EntryWithPlaceholder(master=window, placeholder="Number of tracks to be download", width=40)
number_tracks.grid(row=1, column=3)
album_txt = tk.Label(master=window, text='Download Album')
album_txt.grid(row=2)
album_url = EntryWithPlaceholder(master=window, placeholder="Album Url", width=100)
album_url.grid(row=2, column=1, columnspan=30)
download_status = tk.Label(master=window, text='Not Finished Yet', bg='gray', fg='black', width=40)
download_status.grid(row=3, column=1)
download_btn = tk.Button(master=window, text='Proceed Download', width=60, height=5, bg='green', fg='white')
download_btn.grid(row=3, column=0)


def handle_click(event):
    if not exists(join(abspath('.'), abspath('downloaded'))):
        mkdir('downloaded')
    track_uid['state'] = 'disabled'
    number_tracks['state'] = 'disabled'
    album_url['state'] = 'disabled'
    if track_uid.get() != '' and track_uid.get() != 'User ID':
        uid = track_uid.get()
        n_tracks = number_tracks.get() or 20
        if type(n_tracks) == str:
            if n_tracks == 'Number of tracks to be download':
                n_tracks = 20
            else:
                n_tracks = int(n_tracks)
        download_status["text"] = 'Now Downloading, Pls wait until it done'
        thr = threading.Thread(target=download_tracks, args=[uid, n_tracks])
        thr.start()
        thr.join()
        download_status["text"] = "Finished!"
    elif album_url.get() != '' and album_url.get() != 'Album Url':
        download_status["text"] = 'Now Downloading, Pls wait until it done'
        thr = threading.Thread(target=download_albums, args=[[album_url.get()]])
        thr.start()
        thr.join()
        download_status["text"] = "Finished!"
    else:
        print('Not found')
    track_uid['state'] = 'normal'
    number_tracks['state'] = 'normal'
    album_url['state'] = 'normal'

download_btn.bind("<Button-1>", handle_click)

window.mainloop()