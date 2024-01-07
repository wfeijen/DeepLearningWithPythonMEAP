import os
import math
import shutil
from send2trash import send2trash
from PIL import Image, UnidentifiedImageError, ImageDraw, ImageStat
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

        elips_breedte = breedte * 3 // 4
        elips_hoogte = hoogte * 3 // 4

        links_lijst = [breedte // 8, breedte // 2, breedte * 7 // 8]
        top_lijst = [hoogte // 8, hoogte // 2, hoogte * 7//8]
        combinaties = list(product(links_lijst, top_lijst))
        mean_color = tuple([math.floor(n) for n in ImageStat.Stat(im)._getmean()])
        for links, top in combinaties:
            im_nieuw = im.copy()
            draw = ImageDraw.Draw(im_nieuw)
            #elips_breedte, elips_hoogte = 300, 600  # Size of Bounding Box for ellipse

            bbox = (links - elips_breedte / 2, top - elips_hoogte / 2, links + elips_breedte / 2, top + elips_hoogte / 2)
            draw.ellipse(bbox, fill=mean_color, outline=mean_color)
            nieuwe_file_naam = werk_directory + "/" + "{:06d}".format(filecounter)  + ".jpg"
            im_nieuw.save(nieuwe_file_naam)

            print(str(((filecounter * 1000) // totaal_aantal_resultaat) / 10) + "%")
            filecounter += 1
    except UnidentifiedImageError as e:
        print(oude_file_naam, ' lijkt geen image te zijn. Foutmelding: ', e)


print("Aantal : ", str(filecounter))