import os
import shutil
from send2trash import send2trash
import random
from PIL import Image, UnidentifiedImageError, ImageFilter
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, hashPicture, hash_size, convert_image_to_square
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir, gevonden_hashcodes_onder_dir
from generiekeFuncties.utilities import initializeer_voortgangs_informatie, geeft_voortgangs_informatie
from itertools import product

targetSizeImage = get_target_picture_size()  # Size that the ml engine expects
minimumSizeLongSideImage = targetSizeImage // 2



werk_directory = '/media/willem/KleindSSD/machineLearningPictures/take1/RawInput/wel'

filecounter = 0
gevonden_files = gevonden_files_onder_dir(werk_directory, '.jpg')
totaal_aantal_resultaat = len(gevonden_files)

for oude_file_naam in gevonden_files:
    print(oude_file_naam)
    try:
        im = Image.open(oude_file_naam)
        breedte, hoogte = im.size
        blur_breedte = breedte // 2
        blur_hoogte = hoogte // 2

        links_min = 0
        links_max = breedte - blur_breedte
        top_min = 0
        top_max = hoogte - blur_hoogte
        filecounter += 1
        print(str(((filecounter * 1000) // totaal_aantal_resultaat) / 10) + "%")
        for i in range(4):
            links = random.randint(links_min, links_max)
            top = random.randint(top_min, top_max)
            box = (links, top, links + blur_breedte, top + blur_hoogte)
            im_nieuw = im.copy()
            ic = im_nieuw.crop(box)
            ic = ic.filter(ImageFilter.GaussianBlur(100))
            im_nieuw.paste(ic, box)
            nieuwe_file_naam = werk_directory + "/" + "{:07d}".format(filecounter) + "blur" + str(i) + ".jpg"
            im_nieuw.save(nieuwe_file_naam)

    except UnidentifiedImageError as e:
        print(oude_file_naam, ' lijkt geen image te zijn. Foutmelding: ', e)


print("Aantal : ", str(filecounter))