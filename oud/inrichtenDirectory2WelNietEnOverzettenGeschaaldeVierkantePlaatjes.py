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
from keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt


from send2trash import send2trash

targetSizeImage = 280  # Size that the ml engine expects twice the smallest input image short side
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


def resizeKortsteKantNaarDoelgrootte(im, targetSizeIm):
    x, y = im.size
    s = targetSizeIm * max(im.size) / min(im.size)
    im_out = im
    im_out.thumbnail((s, s), Image.ANTIALIAS)
    return im_out

def showImage(im):
    img_tensor = image.img_to_array(im)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.
    plt.imshow(img_tensor[0])
    plt.show()

def get_square_images(im, targetSizeIm):
    # geeft een vierkant plaatje terug met twee stroken die elk een zo groot mogelijk deel van het origineel bevatten
    # breed: links tot breedte resultaat en vanaf rechts terug
    # hoog: top tot hoogte resultaat en vanaf bodem terug
    # voordeel: elk plaatje blijft alle elementen houden
    quadrant_size = int(targetSizeIm / 2)
    im = resizeKortsteKantNaarDoelgrootte(im, quadrant_size) # origineel op grootte maken
    sx, sy = im.size
    speling = int(max(0, targetSizeImage - max(im.size)) / 2)
    # Leeg image
    antwoord = img = Image.new('RGB', (targetSizeIm, targetSizeIm))
    # buitenkanten bij breed of hoog plaatje
    if sx >= sy : # breed plaatje
        left = max(0, sx - targetSizeIm)
        antwoord.paste(im.crop((0, 0, min(sx, targetSizeIm), quadrant_size)), (speling, 0))
        antwoord.paste(im.crop((left, 0, left + min(sx, targetSizeIm), quadrant_size)), (speling, quadrant_size))
    else:
        top = max(0, sy - targetSizeIm)
        antwoord.paste(im.crop((0, 0, quadrant_size, min(sy, targetSizeIm))), (0, speling))
        antwoord.paste(im.crop((0, top, quadrant_size, top + min(sy, targetSizeIm))), (quadrant_size, speling))
    #showImage(antwoord)
    return antwoord


def make_and_fill_subdirectory(subSubDirName, targetDir, sourceDir, numberOfFiles, fileNames):
    target_data_set_dir = os.path.join(sourceDir, subSubDirName)
    target_sub_dir = os.path.join(targetDir, subSubDirName)
    os.mkdir(target_sub_dir)
    for j in range(0, numberOfFiles):
        file_name = random.choice(fileNames)
        kale_file_naam, file_extension = os.path.splitext(file_name)
        src = os.path.join(target_data_set_dir, file_name)
        im = Image.open(src)
        im = get_square_images(im=im, targetSizeIm=targetSizeImage)
        dst = os.path.join(target_sub_dir, kale_file_naam + file_extension)
        im = im.convert('RGB')
        im.save(dst)
        fileNames.remove(file_name)
    print(target_sub_dir, ' total images:', len(os.listdir(target_sub_dir)))
    return fileNames


nietFileNames = make_and_fill_subdirectory(subSubDirName='niet', targetDir=train_dir, sourceDir=original_data_set_dir,
                                           numberOfFiles=aantalTrain, fileNames=nietFileNames)
nietFileNames = make_and_fill_subdirectory(subSubDirName='niet', targetDir=test_dir, sourceDir=original_data_set_dir,
                                           numberOfFiles=aantalTest, fileNames=nietFileNames)
make_and_fill_subdirectory(subSubDirName='niet', targetDir=validation_dir, sourceDir=original_data_set_dir,
                           numberOfFiles=aantalValidation, fileNames=nietFileNames)
welFileNames = make_and_fill_subdirectory(subSubDirName='wel', targetDir=train_dir, sourceDir=original_data_set_dir,
                                          numberOfFiles=aantalTrain, fileNames=welFileNames)
welFileNames = make_and_fill_subdirectory(subSubDirName='wel', targetDir=test_dir, sourceDir=original_data_set_dir,
                                          numberOfFiles=aantalTest, fileNames=welFileNames)
make_and_fill_subdirectory(subSubDirName='wel', targetDir=validation_dir, sourceDir=original_data_set_dir,
                           numberOfFiles=aantalValidation, fileNames=welFileNames)
