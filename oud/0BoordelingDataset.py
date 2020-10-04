import os
from generiekeFuncties.fileHandlingFunctions import give_list_of_images
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.fileHandlingFunctions import veranderVanKant, markeerGecontroleerd
from generiekeFuncties.utilities import verwijderGecontroleerdeFilesFromList

directoryNr = 2
aantal = 25

onderzoeks_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/rawInput'

imageList_P = [os.path.join(onderzoeks_dir, "wel", fileName) for fileName in
               give_list_of_images(subdirName="wel", baseDir=onderzoeks_dir)]
imageList_P.sort()
imageList_geen_P = [os.path.join(onderzoeks_dir, "niet", fileName) for fileName in
                    give_list_of_images(subdirName="niet", baseDir=onderzoeks_dir)]
imageList_geen_P.sort()

imageList_P = verwijderGecontroleerdeFilesFromList(imageList_P)
imageList_geen_P = verwijderGecontroleerdeFilesFromList(imageList_geen_P)

viewer = Viewer(imgList=imageList_geen_P, titel="NIET", aanleidingTotVeranderen="wel")

viewer = Viewer(imgList=imageList_P, titel="WEL", aanleidingTotVeranderen="niet")
