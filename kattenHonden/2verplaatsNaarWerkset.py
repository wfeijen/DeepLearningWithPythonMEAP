# Maakt directories met positieve en negatieve samples.
# De samples worden gedupliceerd door twee keer te croppen zodat de crops samen het volledige rechthoek vullen
# Vierkante samples worden dus in effect gedupliceerd, maar dat komt niet vaak voor
# De reden hiervan is dat we vervorming willen voorkomen die bij een resize van rechthoek naar vierkant optreed.
# De verdubbeling is natuurlijk ook een soort poor mans augmentation
# Daarnaast vind er een herschaling van originelen plaats om het volume op schijf te beperken

import os
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir, \
    maak_directory_helemaal_leeg, prioriteerGecontroleerd, maak_doeldirectory_en_verplaats_random_files
from generiekeFuncties.plaatjesFuncties import get_target_picture_size
from generiekeFuncties.utilities import geeftVoortgangsInformatie, initializeerVoortgangsInformatie

voortgangs_informatie = initializeerVoortgangsInformatie("start verklein en verplaats")

#aantalSamplesWel = 31000
#aantalSamplesNiet = 16000
percentageTrain = 0.8
percentageTest = 0.1
percentageValidation = 0.1

# The path to the directory where the original
# data set was uncompressed
root = '/mnt/GroteSchijf/machineLearningPictures/kattenHonden'
full_data_set_dir = os.path.join(root, 'OntdubbeldEnVerkleind')
target_base_dir = os.path.join(root, 'Werkplaats')
targetSizeImage = get_target_picture_size()

nietFileNames = gevonden_files_onder_dir(os.path.join(full_data_set_dir, 'niet'), '.jpg')
welFileNames = gevonden_files_onder_dir(os.path.join(full_data_set_dir, 'wel'), '.jpg')
print("aantal Niet totaal:", len(nietFileNames), " aantal Wel totaal:", len(welFileNames))

# Zorgen voor een zekere balans in de samples
aantalSamplesWel = len(welFileNames) // 2
aantalSamplesNiet = len(nietFileNames) // 2
if aantalSamplesWel < aantalSamplesNiet // 2:
    aantalSamplesNiet = 2 * aantalSamplesWel
elif aantalSamplesNiet < aantalSamplesWel // 2:
    aantalSamplesWel = 2 * aantalSamplesNiet

print("aantal Niet geselecteerd:", aantalSamplesNiet, " aantal Wel geselecteerd:", aantalSamplesWel)
aantalSamplesValidation = int(min(aantalSamplesNiet, aantalSamplesWel) * percentageValidation)
aantalSamplesTest = int(min(aantalSamplesNiet, aantalSamplesWel) * percentageTest)
aantalSamplesTrainWel = aantalSamplesWel - aantalSamplesTest - aantalSamplesValidation
aantalSamplesTrainNiet = aantalSamplesNiet - aantalSamplesTest - aantalSamplesValidation

voortgangs_informatie = geeftVoortgangsInformatie("Start leegmaken dirs", voortgangs_informatie)

maak_directory_helemaal_leeg(target_base_dir)
train_dir = os.path.join(target_base_dir, 'train')
os.mkdir(train_dir)
test_dir = os.path.join(target_base_dir, 'test')
os.mkdir(test_dir)
validation_dir = os.path.join(target_base_dir, 'validation')
os.mkdir(validation_dir)


voortgangs_informatie = geeftVoortgangsInformatie("Start niet files", voortgangs_informatie)

nietFileNames = prioriteerGecontroleerd(nietFileNames, aantalSamplesNiet, "n")

nietFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='niet',
                                                             targetDir=train_dir,
                                                             numberOfFiles=aantalSamplesTrainNiet,
                                                             fileNames=nietFileNames)
nietFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='niet',
                                                             targetDir=test_dir,
                                                             numberOfFiles=aantalSamplesTest,
                                                             fileNames=nietFileNames)
nietFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='niet',
                                                             targetDir=validation_dir,
                                                             numberOfFiles=aantalSamplesValidation,
                                                             fileNames=nietFileNames)

voortgangs_informatie = geeftVoortgangsInformatie("Start wel files", voortgangs_informatie)

welFileNames = prioriteerGecontroleerd(welFileNames, aantalSamplesWel, "w")
welFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='wel',
                                                            targetDir=train_dir,
                                                            numberOfFiles=aantalSamplesTrainWel,
                                                            fileNames=welFileNames)
welFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='wel',
                                                            targetDir=test_dir,
                                                            numberOfFiles=aantalSamplesTest,
                                                            fileNames=welFileNames)
welFileNames = maak_doeldirectory_en_verplaats_random_files(subSubDirName='wel',
                                                            targetDir=validation_dir,
                                                            numberOfFiles=aantalSamplesValidation,
                                                            fileNames=welFileNames)

voortgangs_informatie = geeftVoortgangsInformatie("Klaar", voortgangs_informatie)
