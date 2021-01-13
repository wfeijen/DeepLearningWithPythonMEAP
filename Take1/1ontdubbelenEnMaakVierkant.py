import os
import shutil
from send2trash import send2trash
from PIL import Image
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, hashPicture, hash_size, convert_image_to_square
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir, gevonden_hashcodes_onder_dir
from generiekeFuncties.utilities import initializeerVoortgangsInformatie, geeftVoortgangsInformatie

targetSizeImage = get_target_picture_size()  # Size that the ml engine expects
minimumSizeLongSideImage = targetSizeImage // 2



root = '/mnt/GroteSchijf/machineLearningPictures/take1'
input_directory = os.path.join(root, 'RawInput')
output_directory = os.path.join(root, 'OntdubbeldEnVerkleind')
constVerwijzingDir = os.path.join(root, 'Verwijzingen')


def ontdubbel_en_verklein_dir(input_dir, output_dir, subdir,
                              minimum_grootte_Lange_zijde_image,
                              hash_size):
    hashes = set([strHash for strHash in gevonden_hashcodes_onder_dir(output_dir, hash_size)])
    aantal_verplaatste_files = 0
    for oude_file_naam in gevonden_files_onder_dir(os.path.join(input_dir, subdir), '.jpg'):
        print(oude_file_naam)
        im = Image.open(oude_file_naam)
        if max(im.size) >= minimum_grootte_Lange_zijde_image:
            size_x, size_y = im.size
            if not (size_x == targetSizeImage and size_y == targetSizeImage):
                im = convert_image_to_square(im=im, targetsize_im=targetSizeImage)
                send2trash(oude_file_naam)
                im.save(oude_file_naam)
            str_hash = hashPicture(im)
            if str_hash not in hashes:
                hashes.add(str_hash)
                nieuwe_file_naam = os.path.join(output_dir, subdir, str_hash[0], str_hash[1],
                                                str_hash + ".jpg")
                os.makedirs(os.path.dirname(nieuwe_file_naam), exist_ok=True)
                shutil.move(oude_file_naam, nieuwe_file_naam)
                aantal_verplaatste_files = aantal_verplaatste_files + 1
            else:
                shutil.move(oude_file_naam, oude_file_naam + ".bestaatAl.jpg")
        else:
            shutil.move(oude_file_naam, oude_file_naam + ".teKlein.jpg")
    return aantal_verplaatste_files

#Eerst checken of er nog files in verwijzingen staan, verder lengte gelezen hashes checken
nog_te_bekijken_verwijzingen = [os.path.join(constVerwijzingDir, f) for f in os.listdir(constVerwijzingDir)
                                      if os.path.isfile(os.path.join(constVerwijzingDir, f))]
if len(nog_te_bekijken_verwijzingen) > 0:
    print("Er zijn nog te bekijken verwijzingen.")
else:
    voortgangs_informatie = initializeerVoortgangsInformatie("start ontdubbel en verklein")
    ontdubbel_en_verklein_dir(input_directory, output_directory, "niet",
                              minimumSizeLongSideImage, hash_size())
    voortgangs_informatie = geeftVoortgangsInformatie("niet gedaan", voortgangs_informatie)
    ontdubbel_en_verklein_dir(input_directory, output_directory, "wel",
                              minimumSizeLongSideImage, hash_size())
    voortgangs_informatie = geeftVoortgangsInformatie("klaar", voortgangs_informatie)