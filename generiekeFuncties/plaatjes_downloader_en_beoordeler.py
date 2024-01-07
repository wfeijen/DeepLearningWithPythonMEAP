import os
from datetime import datetime
from requests import exceptions
from generiekeFuncties.fileHandlingFunctions import readDictFile, writeDict, dict_values_string_to_int
from generiekeFuncties.plaatjesFuncties import download_image_naar_memory, scherpte_maalGrootte_image, bigHashPicture, sla_image_op, convert_image_to_square, get_target_picture_size

from keras import preprocessing
from tensorflow.keras import applications, models
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m

import numpy as np
from PIL import Image


class Plaatjes_beoordelaar:
    def __init__(self, aantalWelPerNiet, nieuwePlaatjesLocatie, minHoogte, minBreedte,
                min_scherpte_grootte, benaderde_hash_administratie_pad, grenswaarde,
                 model_dir, basis_dir, benaderde_url_administratie_pad):
        self._aantalWelPerNiet = aantalWelPerNiet
        self._nogTeLadenNietCounter = 0
        self._nieuwePlaatjesLocatie = nieuwePlaatjesLocatie
        self._minHoogte = minHoogte
        self._minBreedte = minBreedte
        self._min_scherpte_grootte = min_scherpte_grootte
        self._targetImageSize = get_target_picture_size()
        self._benaderde_hash_administratie_pad = benaderde_hash_administratie_pad
        self._grenswaarde = grenswaarde
        self._hash_administratie = readDictFile(self._benaderde_hash_administratie_pad)
        self._hash_administratie = dict_values_string_to_int(self._hash_administratie)
        self._benaderde_url_administratie_pad = benaderde_url_administratie_pad
        self._url_administratie = readDictFile(self._benaderde_url_administratie_pad)
        self._classifier = models.load_model(model_dir,
                                            custom_objects={'recall_m': recall_m, 'precision_m': precision_m,
                                                            "f2_m": f2_m})
        # Testen of hij goed geinitialiseerd is
        print(str(self.classificeer_vollig_image_from_file(os.path.join(basis_dir, 'maan.jpg'))))

    def laad_en_check_plaatje(self, url_plaatje):
        goed_image = False
        img = None
        nieuwe_file_naam = ""
        hash_groot = 0
        url_plaatje = url_plaatje.replace('%3A', ':').replace('%2F', '/')
        print(url_plaatje)
        if url_plaatje in self._url_administratie:
            print('   is al eens benaderd.')
        else:
            self._url_administratie[url_plaatje] = str(datetime.now())
            writeDict(self._url_administratie, self._benaderde_url_administratie_pad)
            try:
                img = download_image_naar_memory(url_plaatje)
            except exceptions.InvalidURL as e:
                print("   niet leesbaar.")
                print(e)


            if img is None:
                print('   niet gelezen.')
            else:
                breedte, hoogte = img.size
                scherpte = scherpte_maalGrootte_image(im=img)
                print('s: ' + str(scherpte) + ' b: ' + str(breedte) + ' h: ' + str(hoogte))
                hash_groot = bigHashPicture(img)
                if hash_groot == '':
                    print('   wordt overgeslagen omdat de hash niet klopt')
                elif hoogte < self._minHoogte or breedte < self._minBreedte:
                    print('   is te klein.')
                elif scherpte < self._min_scherpte_grootte:
                    print('   scherpte grootte onvoldoende')
                elif hash_groot in self._hash_administratie:
                    if self._hash_administratie[hash_groot] >= scherpte:
                        print('   al eens gevonden.')
                    else:
                        print('   verbeterde scherpte maal grootte')
                        goed_image = True
                else:
                    goed_image = True
        if goed_image:
            self._hash_administratie[hash_groot] = scherpte
            writeDict(self._hash_administratie, self._benaderde_hash_administratie_pad)
            nieuwe_file_naam = "{:06d}".format(breedte) + "x" + "{:06d}".format(hoogte) + "_" + "{:06d}".format(scherpte) + "_" + hash_groot + ".jpg"
        return goed_image, img, nieuwe_file_naam

    def beoordeel_plaatje(self, img, url_plaatje, file_naam):
        resultaat = self.classificeer_vollig_image(img, url_plaatje)
        if resultaat >= self._grenswaarde:
            keuze = 'wel'
            self._nogTeLadenNietCounter += 1
            print('     wel')
        else:
            keuze = 'niet'
            nietPlaatjeLaden = self._nogTeLadenNietCounter >= self._aantalWelPerNiet
            if nietPlaatjeLaden:
                nogTeLadenNietCounter = self._nogTeLadenNietCounter - self._aantalWelPerNiet
                print('     niet, wel geladen')
            else:
                print('     niet, niet geladen')
        if keuze == 'wel' or nietPlaatjeLaden:
            file_naam = os.path.join(self._nieuwePlaatjesLocatie, keuze, file_naam)
            print(file_naam)
            sla_image_op(img, file_naam)

    def classificeer_vollig_image(self, img, kenmerk):
        try:
            img = convert_image_to_square(img, self._targetImageSize)
            pp_image = preprocessing.image.img_to_array(img)
            np_image = np.array(pp_image)
            np_image = np.expand_dims(np.array(np_image).astype(float), axis=0)
            # np_image /= 255.0
            np_image = applications.inception_resnet_v2.preprocess_input(np_image)
            classifications = self._classifier.predict(np_image)
            return classifications[0][0]
        except ValueError as e:
            print('###', kenmerk, ' niet goed verwerkt:', e)
            return -1

    def classificeer_vollig_image_from_file(self, file_name_in):
        img = Image.open(file_name_in)
        return self.classificeer_vollig_image(img, file_name_in)
