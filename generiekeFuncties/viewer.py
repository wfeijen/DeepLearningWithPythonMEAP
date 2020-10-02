import os
from tkinter import ttk, Tk, CENTER
from PIL import ImageTk, Image, UnidentifiedImageError
from generiekeFuncties.fileHandlingFunctions import veranderVanKant, markeerGecontroleerd


class Viewer:
    def __init__(self, imgList, titel, aanleidingTotVeranderen):
        if len(imgList)>0:
            self.index = 0
            self.changeList = []
            self.imageList = imgList
            self.root = Tk()
            self.titel = titel
            self.aanleidingTotVranderen = aanleidingTotVeranderen
            self.root.geometry('1800x1000')
            try:
                stgImg = ImageTk.PhotoImage(Image.open(self.imageList[self.index]))
                self.root.title(self.titel + "      " + self.imageList[self.index])
                self.label = ttk.Label(self.root, image=stgImg)
                self.label.place(relx=0.5, rely=0.5, anchor=CENTER)
            except UnidentifiedImageError as e:
                print("Image niet te openen: ", self.imageList[self.index], " - ", e)

            # close_up
            # rear_view
            # lazy_cat
            # dominant
            # overig
            # geen
            # _sperm
            # _caption
            # _close_up




            nietBtn = ttk.Button(self.root, text="NIET (z)", command=self.niet)
            nietBtn.place(x=1800, y=0)
            verwijderBtn = ttk.Button(self.root, text="VERWIJDER (^)", command=self.verwijder)
            verwijderBtn.place(x=1800, y=30)
            welBtn = ttk.Button(self.root, text="WEL (x)", command=self.wel)
            welBtn.place(x=1800, y=60)
            backBtn = ttk.Button(self.root, text="TERUG (<)", command=self.undo)
            backBtn.place(x=1800, y=90)
            klaarBtn = ttk.Button(self.root, text="VERWERKEN", command=self.verwerken)
            klaarBtn.place(x=1800, y=150)
            klaarBtn = ttk.Button(self.root, text="KLAAR", command=self.klaar)
            klaarBtn.place(x=1800, y=210)
            afbrekenBtn = ttk.Button(self.root, text="AFBREKEN", command=self.afbreken)
            afbrekenBtn.place(x=1800, y=240)
            self.root.bind("<Key>", self.key)
            self.root.mainloop()
        else:
            print("lijst is leeg")

    def verwerken(self):
        print("verwerken Lijst ", self.titel)
        for operatie, filePad in self.changeList:
            print(operatie, " ", filePad)
            if operatie == "verwijder":
                os.remove(filePad)
            elif operatie == self.aanleidingTotVranderen:
                veranderVanKant(filePad)
            else:  # onveranderd maar wel gecontroleerd
                markeerGecontroleerd(filePad)
        self.imageList = self.imageList[self.index:]
        self.index = 0
        self.changeList = []


    def klaar(self):
        self.verwerken()
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
        if self.index == len(self.imageList):
            print("Next had niet gemogen is ongedaan gemaakt.")
        else:
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