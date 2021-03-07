import os
from PIL import Image
from generiekeFuncties.RawTherapeeDefaults import RawTherapeeDefaults
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir

locatie = os.path.expanduser('~/Pictures/In_bewerking')
# locatie = '/mnt/GroteSchijf/PictureStore/2021'
# locatie = '/mnt/GroteSchijf/machineLearningPictures/take1/RawInput'


def voeg_toe_voor_extentie(pad, extentie):
    files = gevonden_files_onder_dir(pad, extentie)
    raw_editor_defaults = RawTherapeeDefaults(extentie)
    for file in files:
        #if 'l29' in file:
            im = Image.open(file)
            raw_editor_defaults.maak_specifiek(file, im.size)


voeg_toe_voor_extentie(locatie, '.jpg')
voeg_toe_voor_extentie(locatie, '.nef')



