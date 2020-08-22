from tkinter import ttk, Tk, CENTER
from PIL import ImageTk, Image

class Viewer:
    def __init__(self, imgList, titel):
        self.lijsVerwerken = False
        if len(imgList)>0:
            self.index = 0
            self.changeList = []
            self.imageList = imgList
            self.root = Tk()
            self.titel = titel
            self.root.geometry('1800x1000')
            stgImg = ImageTk.PhotoImage(Image.open(self.imageList[self.index]))
            self.root.title(self.titel + "      " + self.imageList[self.index])
            self.label = ttk.Label(self.root, image=stgImg)
            self.label.place(relx=0.5, rely=0.5, anchor=CENTER)

            nietBtn = ttk.Button(self.root, text="NIET (z)", command=self.niet)
            nietBtn.place(x=1800, y=0)
            verwijderBtn = ttk.Button(self.root, text="VERWIJDER (^)", command=self.verwijder)
            verwijderBtn.place(x=1800, y=30)
            welBtn = ttk.Button(self.root, text="WEL (x)", command=self.wel)
            welBtn.place(x=1800, y=60)
            backBtn = ttk.Button(self.root, text="TERUG (<)", command=self.undo)
            backBtn.place(x=1800, y=90)
            klaarBtn = ttk.Button(self.root, text="KLAAR", command=self.klaar)
            klaarBtn.place(x=1800, y=150)
            afbrekenBtn = ttk.Button(self.root, text="AFBREKEN", command=self.afbreken)
            afbrekenBtn.place(x=1800, y=180)
            self.root.bind("<Key>", self.key)
            self.root.mainloop()

    def klaar(self):
        self.lijsVerwerken = True
        self.root.destroy()


    def afbreken(self):
        self.root.destroy()


    def setImage(self):
        if self.index < len(self.imageList):
            im = Image.open(self.imageList[self.index])
            stgImg = ImageTk.PhotoImage(im)
            self.label.configure(image=stgImg)
            self.label.image = stgImg
            self.root.title(self.titel + " (" + str(self.index) + " van " +
                            str(len(self.imageList)) + ")    " + self.imageList[self.index])
        else:
            self.root.title(self.titel + "      Alle images verwerkt")

    def nextImage(self):
        if self.index < len(self.imageList):
            self.index = self.index + 1
            self.setImage()

    def niet(self):
        if self.index < len(self.imageList):
            self.changeList.append(("niet", self.imageList[self.index]))
            self.nextImage()

    def verwijder(self):
        if self.index < len(self.imageList):
            self.changeList.append(("verwijder", self.imageList[self.index]))
            self.nextImage()


    def wel(self):
        if self.index < len(self.imageList):
            self.changeList.append(("wel", self.imageList[self.index]))
            self.nextImage()


    def undo(self):
        if self.index>0:
            self.index = self.index - 1
            del self.changeList[-1]
        self.setImage()

    def key(self, event):
        kp = repr(event.keysym)
        print(kp)  # repr(event.char))
        if (kp == '\'z\''):
            self.niet()
        if (kp == '\'Up\''):
            self.verwijder()
        if (kp == '\'x\''):
            self.wel()
        if (kp == '\'Left\''):
            self.undo()
        if (kp == '\'Control_R\''):
            self.root.wm_state('iconic')