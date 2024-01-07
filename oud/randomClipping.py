import os
import shutil
from send2trash import send2trash
from PIL import Image, UnidentifiedImageError
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, hashPicture, hash_size, convert_image_to_square
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir, gevonden_hashcodes_onder_dir
from generiekeFuncties.utilities import initializeer_voortgangs_informatie, geeft_voortgangs_informatie
from itertools import product

targetSizeImage = get_target_picture_size()  # Size that the ml engine expects
minimumSizeLongSideImage = targetSizeImage // 2



werk_directory = '/media/willem/KleindSSD/machineLearningPictures/take1/RawInput/wel'

filecounter = 0
gevonden_files = gevonden_files_onder_dir(werk_directory, '.jpg')
totaal_aantal_resultaat = len(gevonden_files) * 9

for oude_file_naam in gevonden_files:
    print(oude_file_naam)
    try:
        im = Image.open(oude_file_naam)
        breedte, hoogte = im.size
        nieuwe_breedte = breedte // 2
        nieuwe_hoogte = hoogte // 2

        links_lijst = [0, breedte // 4, breedte // 2]
        top_lijst = [0, hoogte // 4, hoogte // 2]
        combinaties = list(product(links_lijst, top_lijst))
        for links, top in combinaties:
            im_nieuw = im.crop((links, top, links + nieuwe_breedte, top + nieuwe_hoogte))
            nieuwe_file_naam = werk_directory + "/" + "{:06d}".format(filecounter) + ".jpg"
            im_nieuw.save(nieuwe_file_naam)
            print(str(((filecounter * 1000) // totaal_aantal_resultaat) / 10) + "%")
            filecounter += 1
    except UnidentifiedImageError as e:
        print(oude_file_naam, ' lijkt geen image te zijn. Foutmelding: ', e)


print("Aantal : ", str(filecounter))