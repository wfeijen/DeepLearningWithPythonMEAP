# Maakt directories met positieve en negatieve samples.
# De samples worden gedupliceerd door twee keer te croppen zodat de crops samen het volledige rechthoek vullen
# Vierkante samples worden dus in effect gedupliceerd, maar dat komt niet vaak voor
# De reden hiervan is dat we vervorming willen voorkomen die bij een resize van rechthoek naar vierkant optreed.
# De verdubbeling is natuurlijk ook een soort poor mans augmentation
# Daarnaast vind er een herschaling van originelen plaats om het volume op schijf te beperken

import os
from generiekeFuncties.fileHandlingFunctions import fill_subdirectory_with_squared_images, give_list_of_images, \
    maak_doeldirectory_en_verplaats_random_files, maak_directory_helemaal_leeg
from generiekeFuncties.plaatjesFuncties import remove_small_images_and_give_list_of_proper_sized_images, get_target_picture_size

import math

targetSizeImage = get_target_picture_size()  # Size that the ml engine expects
minimumSizeShortSideImage = targetSizeImage
maximumSizeShortSideImage = 512
removeSmallFilesFromSource = True
minimaalVerschilInVerhoudingImages = 1.1
percentageTrain = 0.8 #ff
percentageTest = 0.1
percentageValidation = 0.1
maximaalVerschilInVerhoudingAantalImages = 3

# The path to the directory where the original
# data set was uncompressed
root = '/mnt/GroteSchijf/machineLearningPictures/take1'
original_data_set_dir = os.path.join(root, 'rawInput')
copie_verwerkte_data_set = os.path.join(root, 'rawVerwerkt')
full_data_set_dir_te_controleren = os.path.join(root, 'volledigeSetVierBijVierTeControleren')

nietFileNames, verwijderd_vanwege_extentie, verwijderd_vanwege_te_klein, kleiner_gemaakt = \
    remove_small_images_and_give_list_of_proper_sized_images(
        subdir_name='niet', basedir=original_data_set_dir,
        remove_small_files_from_source=removeSmallFilesFromSource,
        minimum_size_short_side_image=minimumSizeShortSideImage,
        maximum_size_short_side_image=maximumSizeShortSideImage)
print("# niet: " + str(len(nietFileNames)) + "  -ext: " + str(verwijderd_vanwege_extentie) + " - klein: " + str(
    verwijderd_vanwege_te_klein) + " kleiner: " + str(kleiner_gemaakt))
welFileNames, verwijderd_vanwege_extentie, verwijderd_vanwege_te_klein, kleiner_gemaakt = \
    remove_small_images_and_give_list_of_proper_sized_images(
        subdir_name='wel', basedir=original_data_set_dir,
        remove_small_files_from_source=removeSmallFilesFromSource,
        minimum_size_short_side_image=minimumSizeShortSideImage,
        maximum_size_short_side_image=maximumSizeShortSideImage)
print("# wel:  " + str(len(welFileNames)) + "  -ext: " + str(verwijderd_vanwege_extentie) + " - klein: " + str(
    verwijderd_vanwege_te_klein) + " kleiner: " + str(kleiner_gemaakt))

aantalNiet = len(give_list_of_images(subdirName="niet", baseDir=copie_verwerkte_data_set))
aantalWel = len(give_list_of_images(subdirName="wel", baseDir=copie_verwerkte_data_set))

print("Totaal aantal orignelen niet: ", str(aantalNiet))
print("Totaal aantal orignelen wel: ", str(aantalWel))

# Nu gaan we omzetten naar vierkant en overzetten naar volledige set
fill_subdirectory_with_squared_images(subSubDirName='niet',
                                      targetDir=full_data_set_dir_te_controleren,
                                      sourceDir=original_data_set_dir,
                                      fileNames=nietFileNames,
                                      rawVerwerktDir=copie_verwerkte_data_set,
                                      targetSizeImage=minimumSizeShortSideImage)
fill_subdirectory_with_squared_images(subSubDirName='wel',
                                      targetDir=full_data_set_dir_te_controleren,
                                      sourceDir=original_data_set_dir,
                                      fileNames=welFileNames,
                                      rawVerwerktDir=copie_verwerkte_data_set,
                                      targetSizeImage=minimumSizeShortSideImage)



