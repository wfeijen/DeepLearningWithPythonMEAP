import os
from tkinter import ttk, Tk, CENTER
from PIL import ImageTk, Image, UnidentifiedImageError
from generiekeFuncties.fileHandlingFunctions import veranderVanKant, markeerGecontroleerd

def rgb_naar_hex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

class Viewer:
    def __init__(self, imgList, titel, aanleidingTotVeranderen, breedte, hoogte):
        if len(imgList)>0:
            self.index = 0
            self.changeList = []
            self.imageList = imgList
            self.root = Tk()
            self.titel = titel
            self.aanleidingTotVranderen = aanleidingTotVeranderen
            geometrie = str(breedte) + "x" + str(hoogte)
            self.breedte = breedte
            self.hoogte = hoogte
            self.root.geometry(geometrie)
            try:
                img = Image.open(self.imageList[self.index])
                imGrootte = img.size
                vergroting = min(breedte / img.size[0], hoogte / img.size[1])
                nieuweGrootte = (int(img.size[0] * vergroting), int(img.size[1] * vergroting))
                img = img.resize(nieuweGrootte, Image.BICUBIC)
                stgImg = ImageTk.PhotoImage(img)
                self.root.title(self.titel + str(imGrootte) +
                " [" + str(self.index) + " van " + str(len(self.imageList)) + "]    " +
                "      " + self.imageList[self.index])
                self.label = ttk.Label(self.root, image=stgImg)
                self.label.place(relx=0.5, rely=0.5, anchor=CENTER)
            except UnidentifiedImageError as e:
                print("Image niet te openen: ", self.imageList[self.index], " - ", e)

            nietBtn = ttk.Button(self.root, text="NIET (z)", command=self.niet)
            nietBtn.place(x=breedte, y=0)
            verwijderBtn = ttk.Button(self.root, text="VERWIJDER (^)", command=self.verwijder)
            verwijderBtn.place(x=breedte, y=30)
            welBtn = ttk.Button(self.root, text="WEL (x)", command=self.wel)
            welBtn.place(x=breedte, y=60)
            backBtn = ttk.Button(self.root, text="TERUG (<)", command=self.undo)
            backBtn.place(x=breedte, y=90)
            verwerkenBtn = ttk.Button(self.root, text="VERWERKEN", command=self.verwerken)
            verwerkenBtn.place(x=breedte, y=400)
            klaarBtn = ttk.Button(self.root, text="KLAAR", command=self.klaar)
            klaarBtn.place(x=breedte, y=610)
            afbrekenBtn = ttk.Button(self.root, text="AFBREKEN", command=self.afbreken)
            afbrekenBtn.place(x=breedte, y=640)
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
                print(veranderVanKant(filePad, operatie))
            else:  # onveranderd maar wel gecontroleerd
                print(markeerGecontroleerd(filePad, operatie))
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
            image_path = self.imageList[self.index]
            im = Image.open(image_path)
            imGrootte = im.size
            vergroting = min(self.breedte / im.size[0], self.hoogte / im.size[1])
            nieuweGrootte = (int(im.size[0] * vergroting), int(im.size[1] * vergroting))
            im = im.resize(nieuweGrootte, Image.BICUBIC)
            stgImg = ImageTk.PhotoImage(im)
            self.label.configure(image=stgImg)
            self.label.image = stgImg
            self.root.title(self.titel + str(imGrootte) +
                " [" + str(self.index) + " van " + str(len(self.imageList)) + "]    " +
                image_path)
            self.root.configure(bg=rgb_naar_hex(((100 + 10 * self.index % 3), 100 + 10 * ((self.index + 1) % 3), 100 + 10 * ((self.index + 2) % 3))))
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
        if (kp == '\'Shift_R\''):
            self.root.wm_state('iconic')