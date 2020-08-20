from tkinter import ttk, Tk
from PIL import ImageTk, Image

class Viewer:
    def __init__(self, imgList):
        self.index = 0
        self.lijsVerwerken = False
        self.changeList = []
        self.imageList = imgList
        self.root = Tk()

        self.root.geometry('1200x1000')

        stgImg = ImageTk.PhotoImage(Image.open(self.imageList[self.index]))
        self.label = ttk.Label(self.root, image=stgImg)
        self.label.place(x=0, y=0)

        overslaanBtn = ttk.Button(self.root, text="OVERSLAAN", command=self.overslaan)
        overslaanBtn.place(x=1100, y=0)
        veranderBtn = ttk.Button(self.root, text="VERANDER", command=self.verander)
        veranderBtn.place(x=1100, y=30)
        backBtn = ttk.Button(self.root, text="TERUG", command=self.undo)
        backBtn.place(x=1100, y=60)
        backBtn = ttk.Button(self.root, text="KLAAR", command=self.klaar)
        backBtn.place(x=1100, y=120)
        backBtn = ttk.Button(self.root, text="AFBREKEN", command=self.afbreken)
        backBtn.place(x=1100, y=150)
        self.root.mainloop()


    def klaar(self):
        global lijsVerwerken
        lijsVerwerken = True
        self.root.destroy()


    def afbreken(self):
        self.root.destroy()


    def setImage(self):
        if self.index < len(self.imageList):
            im = Image.open(self.imageList[self.index])
            stgImg = ImageTk.PhotoImage(im)
            self.label.configure(image=stgImg)
            self.label.image = stgImg
        else:
            self.klaar()

    def nextImage(self):
        self.index = self.index + 1
        self.setImage()

    def overslaan(self):
        self.changeList.append(("niks doen", self.imageList[self.index]))
        self.nextImage()

    def verwijder(self):
        self.changeList.append(("verwijder", self.imageList[self.index]))
        self.nextImage()


    def verander(self):
        global changeList
        self.changeList.append(("verander", self.imageList[self.index]))
        self.nextImage()


    def undo(self):
        if self.index>0:
            self.index = self.index - 1
            del self.changeList[-1]
        self.setImage()

