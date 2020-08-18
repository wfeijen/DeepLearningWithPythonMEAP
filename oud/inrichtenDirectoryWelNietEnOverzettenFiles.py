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
maximaalVerschilInVerhoudingAantalImages = 3
original_data_set_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
target_base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'

original_data_set_dir = os.path.join(original_data_set_dir, 'rawInput')
reserve_copie_originele_data_set = os.path.join(original_data_set_dir, 'rawVerwerkt')
full_data_set_dir = os.path.join(original_data_set_dir, 'volledigeSetVierBijVier')


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


def get_single_squared_piece(im, targetSizeIm, crop_region):
    im_out = im.crop(crop_region)
    im_out.thumbnail((targetSizeIm, targetSizeIm), Image.ANTIALIAS)
    return im_out


def get_square_images(im, targetSizeIm):
    # returns a square part of the image sized to target size
    sx, sy = im.size
    antwoord = []
    # buitenkanten bij breed of hoog plaatje
    if sx >= (sy * minimaalVerschilInVerhoudingImages):
        left = sx - sy
        antwoord.append(get_single_squared_piece(im, targetSizeIm, (0, 0, sy, sy)))
        antwoord.append(get_single_squared_piece(im, targetSizeIm, (left, 0, left + sy, sy)))
    elif (sx * minimaalVerschilInVerhoudingImages)<= sy:
        top = sy - sx
        antwoord.append(get_single_squared_piece(im, targetSizeIm, (0, 0, sx, sx)))
        antwoord.append(get_single_squared_piece(im, targetSizeIm, (0, top, sx, top + sx)))
    # en altijd het centrum omdat daar meestal de meeste inforamtie is
    if sx > sy:
        left = (sx - sy) / 2
        antwoord.append(get_single_squared_piece(im, targetSizeIm, (left, 0, left + sy, sy)))
    else:
        top = (sy - sx) / 2
        antwoord.append(get_single_squared_piece(im, targetSizeIm, (0, top, sx, top + sx)))
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
        im_list = get_square_images(im=im, targetSizeIm=targetSizeImage)
        i = 0
        for im in im_list:
            i = i+1
            dst = os.path.join(target_sub_dir, kale_file_naam + str(i) + file_extension)
            im = im.convert('RGB')
            im.save(dst)
        fileNames.remove(file_name)
    print(target_sub_dir, ' total images:', len(os.listdir(target_sub_dir)))
    return fileNames


shutil.rmtree(target_base_dir)
os.mkdir(target_base_dir)

train_dir = os.path.join(target_base_dir, 'train')
os.mkdir(train_dir)
validation_dir = os.path.join(target_base_dir, 'validation')
os.mkdir(validation_dir)
test_dir = os.path.join(target_base_dir, 'test')
os.mkdir(test_dir)

nietFileNames = give_list_of_images(subdirName='niet', baseDir=original_data_set_dir)
welFileNames = give_list_of_images(subdirName='wel', baseDir=original_data_set_dir)

aantalSamplesWel = len(welFileNames)
aantalSamplesNiet = len(nietFileNames)

if aantalSamplesWel >= aantalSamplesNiet:
    aantalSamplesWel = min(aantalSamplesWel, aantalSamplesNiet * maximaalVerschilInVerhoudingAantalImages)
else:
    aantalSamplesNiet = min(aantalSamplesNiet, aantalSamplesWel * maximaalVerschilInVerhoudingAantalImages)

aantalSamplesTrainWel = math.floor(percentageTrain * aantalSamplesWel)
aantalSamplesTestWel = math.floor(percentageTest * aantalSamplesWel)

aantalSamplesTrainNiet = math.floor(percentageTrain * aantalSamplesNiet)
aantalSamplesTestNiet = math.floor(percentageTest * aantalSamplesNiet)
aantalSamplesValidation = min(aantalSamplesNiet - aantalSamplesTrainNiet - aantalSamplesTestNiet,
                              aantalSamplesWel - aantalSamplesTrainWel - aantalSamplesTestWel)

nietFileNames = fileHandlingFunctions.maak_doeldirectory_en_verplaats_random_files(subSubDirName='niet',
                                                                                   sourceDir=full_data_set_dir,
                                                                                   targetDir=train_dir,
                                                                                   numberOfFiles=aantalSamplesTrainNiet,
                                                                                   fileNames=nietFileNames)
nietFileNames = make_and_fill_subdirectory(subSubDirName='niet', targetDir=test_dir, sourceDir=original_data_set_dir,
                                           numberOfFiles=aantalSamplesTestNiet, fileNames=nietFileNames)
make_and_fill_subdirectory(subSubDirName='niet', targetDir=validation_dir, sourceDir=original_data_set_dir,
                           numberOfFiles=aantalSamplesValidation, fileNames=nietFileNames)
welFileNames = make_and_fill_subdirectory(subSubDirName='wel', targetDir=train_dir, sourceDir=original_data_set_dir,
                                          numberOfFiles=aantalSamplesTrainWel, fileNames=welFileNames)
welFileNames = make_and_fill_subdirectory(subSubDirName='wel', targetDir=test_dir, sourceDir=original_data_set_dir,
                                          numberOfFiles=aantalSamplesTestWel, fileNames=welFileNames)
make_and_fill_subdirectory(subSubDirName='wel', targetDir=validation_dir, sourceDir=original_data_set_dir,
                           numberOfFiles=aantalSamplesValidation, fileNames=welFileNames)
