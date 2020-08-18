# Maakt directories met positieve en negatieve samples.
# De samples worden gedupliceerd door twee keer te croppen zodat de crops samen het volledige rechthoek vullen
# Vierkante samples worden dus in effect gedupliceerd, maar dat komt niet vaak voor
# De reden hiervan is dat we vervorming willen voorkomen die bij een resze van rechthoek naar vierkant optreed.
# De verdubbeling is natuurlijk ook een soort poor mans augmentation
# Daarnaast vind er een herschaling van originelen plaats om het volume op schijf te beperken

import os, errno
import shutil
import math
import random
from PIL import Image
from send2trash import send2trash

targetSizeImage = 140  # Size that the ml engine expects
maxAantalSamplesPerCategorie = 30000
percentageTrain = 0.8
percentageTest = 0.1
percentageValidation = 0.1
minimumSizeShortSideImage = targetSizeImage
removeSmallFilesFromSource = True
minimaalVerschilInVerhoudingImages = 1.2

# The path to the directory where the original
# data set was uncompressed
original_data_set_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def give_list_of_images(subdirName, baseDir):
    data_set_dir = os.path.join(baseDir, subdirName)
    file_names = [f for f in os.listdir(data_set_dir) if os.path.isfile(os.path.join(data_set_dir, f))]
    return file_names


nietFileNames = give_list_of_images(subdirName='niet', baseDir=original_data_set_dir)
welFileNames = give_list_of_images(subdirName='wel', baseDir=original_data_set_dir)

aantalSamplesPerKant = min(len(welFileNames), len(nietFileNames), maxAantalSamplesPerCategorie)
aantalTrain = math.floor(percentageTrain * aantalSamplesPerKant)
aantalTest = math.floor(percentageTest * aantalSamplesPerKant)
aantalValidation = aantalSamplesPerKant - aantalTest - aantalTrain

# The directory where we will
# store our ordered data set
target_base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
shutil.rmtree(target_base_dir)
os.mkdir(target_base_dir)

train_dir = os.path.join(target_base_dir, 'train')
os.mkdir(train_dir)
validation_dir = os.path.join(target_base_dir, 'validation')
os.mkdir(validation_dir)
test_dir = os.path.join(target_base_dir, 'test')
os.mkdir(test_dir)

maxVerhouding = 1

def zoek_maximale_verhouding(subSubDirName, sourceDir, fileNames, maxVerhouding):
    target_data_set_dir = os.path.join(sourceDir, subSubDirName)
    for file_name in fileNames:
        kale_file_naam, file_extension = os.path.splitext(file_name)
        src = os.path.join(target_data_set_dir, file_name)
        im = Image.open(src)
        x, y = im.size
        x = float(x)
        y = float(y)
        verhouding = max(x/y, y/x)
        if verhouding > maxVerhouding:
            print(verhouding)
            maxVerhouding = verhouding
    return fileNames


zoek_maximale_verhouding(subSubDirName='wel', sourceDir=original_data_set_dir, fileNames=welFileNames, maxVerhouding=maxVerhouding)
zoek_maximale_verhouding(subSubDirName='niet', sourceDir=original_data_set_dir, fileNames=nietFileNames, maxVerhouding=maxVerhouding)
