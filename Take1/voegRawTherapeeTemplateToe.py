import os, errno
import shutil
from PIL import Image, ImageStat

# root/level1/naam###blaadjes --> root/level1/naam/blaadjes
# recursief alle filenamen ophalen

fileNames = []
rt = os.path.expanduser('~/VMuitwisseling/x')

templateFile = open("../generiekeFuncties/rawtherapeeJPGtemplate.pp3")
template = templateFile.read()
templateFile.close()

validFileExtensions = [".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".png"]

factor = 16/9

for root, dummy_directories, filenames in os.walk(rt):
     for filename in filenames:
             fileNames.append((root, filename))

imageFiles = [os.path.join(pad, filenaam) for pad, filenaam in fileNames
              if os.path.splitext(filenaam)[1].lower() in validFileExtensions]

for imageFile in imageFiles:
    img = Image.open(imageFile)
    breedte, hoogte = img.size
    if breedte > hoogte * factor:
        breedte = hoogte * factor
    else:
        hoogte = int(breedte / factor)
    inhoudPP3 = template.replace("teVervangenBreedte", str(breedte)).replace("teVervangenHoogte", str(hoogte))
    pp3FileNaam = imageFile + ".pp3"
    pp3File = open(pp3FileNaam, "w")
    pp3File.write(inhoudPP3)
    pp3File.close()
    i=1
