import os
from generiekeFuncties.fileHandlingFunctions import give_list_of_images
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.fileHandlingFunctions import veranderVanKant, markeerGecontroleerd

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
onderzoeks_dir = os.path.join(base_dir, 'programmatest')

imageList_P = [os.path.join(onderzoeks_dir, "wel", fileName) for fileName in
               give_list_of_images(subdirName="wel", baseDir=onderzoeks_dir)]
imageList_geen_P = [os.path.join(onderzoeks_dir, "niet", fileName) for fileName in
                    give_list_of_images(subdirName="niet", baseDir=onderzoeks_dir)]

def verwijderGecontroleerdeFiles(fileList):
    dummy = []
    for file in fileList:
        if len(file)<18:
            dummy.append(file)
        elif file[:18] == "_gecontroleerd.jpg":
            dummy.append(file)

imageList_P = verwijderGecontroleerdeFiles(imageList_P)
imageList_geen_P = verwijderGecontroleerdeFiles(imageList_geen_P)

viewer = Viewer(imgList=imageList_P, titel="WEL")

print("verwerken Lijst ", str(viewer.lijsVerwerken))
if viewer.lijsVerwerken:
    for operatie, filePad in viewer.changeList:
        print(operatie, " ", filePad)
        if operatie == "verwijder":
            os.remove(filePad)
        elif operatie == "verander":
            veranderVanKant(filePad)
        else: # onveranderd maar wel gecontroleerd
            markeerGecontroleerd(filePad)

viewer = Viewer(imgList=imageList_geen_P, titel="NIET")

print("verwerken Lijst ", str(viewer.lijsVerwerken))
if viewer.lijsVerwerken:
    for operatie, filePad in viewer.changeList:
        print(operatie, " ", filePad)
        if operatie == "verwijder":
            os.remove(filePad)
        elif operatie == "verander":
            veranderVanKant(filePad)
        else: # onveranderd maar wel gecontroleerd
            markeerGecontroleerd(filePad)