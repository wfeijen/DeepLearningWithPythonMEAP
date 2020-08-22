# Maakt directories met positieve en negatieve samples.
# De samples worden gedupliceerd door twee keer te croppen zodat de crops samen het volledige rechthoek vullen
# Vierkante samples worden dus in effect gedupliceerd, maar dat komt niet vaak voor
# De reden hiervan is dat we vervorming willen voorkomen die bij een resize van rechthoek naar vierkant optreed.
# De verdubbeling is natuurlijk ook een soort poor mans augmentation
# Daarnaast vind er een herschaling van originelen plaats om het volume op schijf te beperken

import os
from generiekeFuncties.fileHandlingFunctions import give_list_of_images, maak_doeldirectory_en_verplaats_random_files,\
    maak_directory_helemaal_leeg, prioriteerGecontroleerd

import math

maximumAantalFilesPerKant = 12000
percentageTrain = 0.8
maximumAantalFilesPerKant = int(maximumAantalFilesPerKant / percentageTrain)
percentageTest = 0.1
percentageValidation = 0.1
maximaalVerschilInVerhoudingAantalImages = 1.1

# The path to the directory where the original
# data set was uncompressed
root = '/mnt/GroteSchijf/machineLearningPictures/take1'
full_data_set_dir = os.path.join(root, 'volledigeSetVierBijVier')
target_base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'

maak_directory_helemaal_leeg(target_base_dir)
train_dir = os.path.join(target_base_dir, 'train')
os.mkdir(train_dir)
test_dir = os.path.join(target_base_dir, 'test')
os.mkdir(test_dir)
validation_dir = os.path.join(target_base_dir, 'validation')
os.mkdir(validation_dir)

nietFileNames = give_list_of_images(subdirName='niet', baseDir=full_data_set_dir)
welFileNames = give_list_of_images(subdirName='wel', baseDir=full_data_set_dir)

aantalSamplesWel = min(len(welFileNames), maximumAantalFilesPerKant)
aantalSamplesNiet = min(len(nietFileNames), maximumAantalFilesPerKant)

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

print("############ niet filenames #############")
nietFileNames = prioriteerGecontroleerd(nietFileNames, aantalSamplesNiet)
nietFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='niet',
                                                             sourceDir=full_data_set_dir,
                                                             targetDir=train_dir,
                                                             numberOfFiles=aantalSamplesTrainNiet,
                                                             fileNames=nietFileNames)
nietFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='niet',
                                                             sourceDir=full_data_set_dir,
                                                             targetDir=test_dir,
                                                             numberOfFiles=aantalSamplesTestNiet,
                                                             fileNames=nietFileNames)
nietFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='niet',
                                                             sourceDir=full_data_set_dir,
                                                             targetDir=validation_dir,
                                                             numberOfFiles=aantalSamplesValidation,
                                                             fileNames=nietFileNames)
print("############ wel filenames #############")
welFileNames = prioriteerGecontroleerd(welFileNames, aantalSamplesWel)
welFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='wel',
                                                             sourceDir=full_data_set_dir,
                                                             targetDir=train_dir,
                                                             numberOfFiles=aantalSamplesTrainWel,
                                                             fileNames=welFileNames)
welFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='wel',
                                                             sourceDir=full_data_set_dir,
                                                             targetDir=test_dir,
                                                             numberOfFiles=aantalSamplesTestWel,
                                                             fileNames=welFileNames)
welFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='wel',
                                                             sourceDir=full_data_set_dir,
                                                             targetDir=validation_dir,
                                                             numberOfFiles=aantalSamplesValidation,
                                                             fileNames=welFileNames)
