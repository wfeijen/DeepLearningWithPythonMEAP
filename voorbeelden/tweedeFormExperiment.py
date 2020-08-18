from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image


def TestLogic():
    stgImg = ImageTk.PhotoImage(Image.open("../plaatje1.jpg"))
    label.configure(image=stgImg)
    label.image = stgImg


root = Tk()

root.geometry('1010x740+200+200')

stgImg = ImageTk.PhotoImage(Image.open("../plaatje2.jpg"))
label = ttk.Label(root, image=stgImg)
label.place(x=400, y=400)

testBtn = ttk.Button(root, text="TEST", command=TestLogic)
testBtn.place(x=400, y=200)
root.mainloop()
