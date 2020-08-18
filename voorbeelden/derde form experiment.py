#! /usr/bin/env python3

# from tkinter import *
from tkinter import ttk, Tk
from PIL import ImageTk, Image

class Picture:
    def __init__(self, parent):
        self.parent = parent
        img = ImageTk.PhotoImage(Image.open("../plaatje1.jpg"))
        self.label = ttk.Label(self.parent)
        self.label['image'] = img
        img.image = img
        self.label.pack()

        btn = ttk.Button(self.parent, command=self.update, text='Test').pack(side='bottom', pady=50)

    def update(self):
        img = ImageTk.PhotoImage(Image.open("../plaatje2.jpg"))
        self.label['image'] = img
        img.image = img


def main():
    root = Tk()
    root.geometry('400x400+50+50')
    Picture(root)
    root.mainloop()


main()