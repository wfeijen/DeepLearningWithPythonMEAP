import os
# from tkinter import *
from tkinter import ttk, Tk
from PIL import ImageTk, Image
from generiekeFuncties.fileHandlingFunctions import give_list_of_images

# from generiekeFuncties.viewer import Viewer
# from generiekeFuncties.plaatjesWindowClass import PlaatjesWindow


# Wat willen we bekijken?
# train: 0
# test: 1
# validatie: 2
# oorspronkelijke bron: 3
directoryNr = 2
aantal = 25

# [[ 42397   1483]
# [  1955 180209]]

base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
oorspronkelijke_bron_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/volledigeSetVierBijVier'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
if directoryNr == 0:
    onderzoeks_dir = train_dir
elif directoryNr == 1:
    onderzoeks_dir = test_dir
elif directoryNr == 2:
    onderzoeks_dir = validation_dir
else:
    onderzoeks_dir = oorspronkelijke_bron_dir

imageList_P = [os.path.join(onderzoeks_dir, "wel", fileName) for fileName in
               give_list_of_images(subdirName="wel", baseDir=onderzoeks_dir)]
imageList_geen_P = [os.path.join(onderzoeks_dir, "niet", fileName) for fileName in
                    give_list_of_images(subdirName="niet", baseDir=onderzoeks_dir)]

imageList = imageList_geen_P

index = 0

changeList = []


# root = Tk()

# Viewer(root, []).pack(side="top", fill="both", expand=True)

# root.mainloop()

def beeindig():
    root.destroy()


def setImage():
    if index < len(imageList):
        im = Image.open(imageList[index])
        stgImg = ImageTk.PhotoImage(im)
        label.configure(image=stgImg)
        label.image = stgImg
    else:
        beeindig()

def nextImage():
    global index
    index = index + 1
    setImage()

def overslaan():
    global changeList
    changeList.append(("niks doen", imageList[index]))
    nextImage()

def verwijder():
    global changeList
    changeList.append(("verwijder", imageList[index]))
    nextImage()


def verander():
    global changeList
    changeList.append(("verander", imageList[index]))
    nextImage()


def undo():
    global changeList
    global index
    if index>0:
        index = index - 1
        del changeList[-1]
    setImage()


root = Tk()

root.geometry('1200x1000')

stgImg = ImageTk.PhotoImage(Image.open(imageList[index]))
label = ttk.Label(root, image=stgImg)
label.place(x=0, y=0)

overslaanBtn = ttk.Button(root, text="OVERSLAAN", command=overslaan)
overslaanBtn.place(x=1100, y=0)
veranderBtn = ttk.Button(root, text="VERANDER", command=verander)
veranderBtn.place(x=1100, y=30)
backBtn = ttk.Button(root, text="TERUG", command=undo)
backBtn.place(x=1100, y=60)
backBtn = ttk.Button(root, text="KLAAR", command=undo)
backBtn.place(x=1100, y=120)
backBtn = ttk.Button(root, text="AFBREKEN", command=undo)
backBtn.place(x=1100, y=150)
root.mainloop()
