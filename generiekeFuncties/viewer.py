import tkinter as tk

class Viewer(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #self.imageList = imageNames
        self.parent = parent
        self.parent.geometry('1010x740+0+200')

    def TestLogic(self):
        global index
        index = index + 1
        im = Image.open(imageList[index])
        stgImg = ImageTk.PhotoImage(im)
        label.configure(image=stgImg)
        label.image = stgImg


    def Verwijder(self):
        global changeList
        changeList.append("verwijder", )

Class