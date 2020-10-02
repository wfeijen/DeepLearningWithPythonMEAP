import os
import math
import shutil
from send2trash import send2trash
from PIL import Image
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, hashPicture, hash_size
from generiekeFuncties.fileHandlingFunctions import give_list_of_images
from generiekeFuncties.utilities import initializeerVoortgangsInformatie, geeftVoortgangsInformatie, checkGecontroleerd

targetSizeImage = get_target_picture_size()  # Size that the ml engine expects
minimumSizeLongSideImage = targetSizeImage / 2
maximumSizeShortSideImage = 512


root = '/mnt/GroteSchijf/machineLearningPictures/take1'
input_directory = os.path.join(root, 'rawInput')
output_directory = os.path.join(root, 'ontdubbeldEnVerkleind')

def gevonden_hashcodes_onder_dir(onderzoeksDir, hash_size):
    result = [f[:hash_size * 2] for dp, dn, filenames in os.walk(onderzoeksDir) for f in filenames]
    return result

def ontdubbel_en_verklein_dir(input_dir, output_dir, subdir,
                              minimum_grootte_Lange_zijde_image, maximum_size_short_side_image,
                              hash_size):
    hashes = set([strHash for strHash in gevonden_hashcodes_onder_dir(output_dir, hash_size)])
    for file in give_list_of_images(input_dir, subdir):
        oude_file_naam = os.path.join(input_dir, subdir, file)
        im = Image.open(oude_file_naam)
        size = im.size
        if max(size) >= minimum_grootte_Lange_zijde_image:
            if min(size) > maximum_size_short_side_image:
                size = math.ceil(maximum_size_short_side_image * max(size) / min(size))
                im.thumbnail((size, size), Image.BICUBIC)
                im = im.convert('RGB')
                send2trash(oude_file_naam)
                im.save(oude_file_naam)
            str_hash = hashPicture(im)
            if str_hash not in hashes:
                hashes.add(str_hash)
                if checkGecontroleerd(file):
                    nieuwe_file_naam = os.path.join(output_dir, subdir, str_hash + "gecontroleerd.jpg")
                else:
                    nieuwe_file_naam = os.path.join(output_dir, subdir, str_hash + ".jpg")
                shutil.move(oude_file_naam, nieuwe_file_naam)
            else:
                shutil.move(oude_file_naam, oude_file_naam + ".bestaatAl.jpg")
        else:
            shutil.move(oude_file_naam, oude_file_naam + ".teKlein.jpg")

voortgangs_informatie = initializeerVoortgangsInformatie("start ontdubbel en verklein")
ontdubbel_en_verklein_dir(input_directory, output_directory, "niet",
                          minimumSizeLongSideImage, maximumSizeShortSideImage, hash_size())
voortgangs_informatie = geeftVoortgangsInformatie("niet gedaan", voortgangs_informatie)
ontdubbel_en_verklein_dir(input_directory, output_directory, "wel",
                          minimumSizeLongSideImage, maximumSizeShortSideImage, hash_size())
voortgangs_informatie = geeftVoortgangsInformatie("klaar", voortgangs_informatie)