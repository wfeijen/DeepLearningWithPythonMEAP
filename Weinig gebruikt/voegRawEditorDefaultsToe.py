from PIL import Image
from generiekeFuncties.RawTherapeeDefaults import RawTherapeeDefaults
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir

# plunderen directory
files = gevonden_files_onder_dir('/mnt/GroteSchijf/machineLearningPictures/take1/RawInput', '.jpg')
rawEditorDefaults = RawTherapeeDefaults()

for file in files:
    im = Image.open(file)
    rawEditorDefaults.maak_specifiek(file, im.size)