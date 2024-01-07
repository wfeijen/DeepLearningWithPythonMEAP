import os
import sys


sys.path.insert(0, os.getcwd())

from generiekeFuncties.fileHandlingFunctions import (
    gevonden_files_onder_dir,
    readDictFile,
    write_na_te_lopen_verwijzingen_directorie,
    silentremove,
)
from generiekeFuncties.viewer import Viewer


from generiekeFuncties.plaatjesFuncties import bigHash_size


directoryNr = 2
aantal = 25
hash_size = bigHash_size()

base_dir = "/media/willem/KleindSSD/machineLearningPictures/take1"
onderzoeks_dir = os.path.join(base_dir, "RawInput")
constVerwijzingDir = os.path.join(base_dir, "VerwijzingenBoekhouding")
constWelDir = os.path.join(onderzoeks_dir, "wel")
constNietDir = os.path.join(onderzoeks_dir, "niet")

controleText = "_gecontroleerd_"
imageList_P = [
    f for f in gevonden_files_onder_dir(constWelDir, ".jpg") if controleText not in f
]
imageList_P.sort()
imageList_geen_P = [
    f for f in gevonden_files_onder_dir(constNietDir, ".jpg") if controleText not in f
]
imageList_geen_P.sort()
dummyX = Viewer(imgList=imageList_geen_P, titel="NIET", aanleidingTotVeranderen="wel")
dummyX = None
dummyY = Viewer(imgList=imageList_P, titel="WEL", aanleidingTotVeranderen="niet")
dummyY = None


# Testen of er nog files niet gecontroleerd zijn
lijst_niet_gecontroleerd = [
    f for f in gevonden_files_onder_dir(constWelDir, ".jpg") if controleText not in f
]
lijst_niet_gecontroleerd.extend(
    [f for f in gevonden_files_onder_dir(constNietDir, ".jpg") if controleText not in f]
)

if len(lijst_niet_gecontroleerd) > 0:
    print("Er moeten nog " + str(len(lijst_niet_gecontroleerd)) + " gecontroleerd.")
