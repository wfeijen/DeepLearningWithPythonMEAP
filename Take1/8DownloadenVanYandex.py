import regex
import os
import itertools
import time
from tensorflow.keras import models
from generiekeFuncties.fileHandlingFunctions import readDictFile, writeDict, lees_file_regels_naar_ontdubbelde_lijst
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image, download_image_naar_memory, sla_image_op, bigHashPicture, classificeer_vollig_image_from_file
from datetime import datetime, timedelta
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m
from numpy.random import exponential
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from requests import exceptions
from generiekeFuncties.RawTherapeeDefaults import RawTherapeeDefaults
import random
import sys
from generiekeFuncties.queryResultaatScherm import QueryResultaatScherm

minBreedte = 800
minHoogte = 1000
maxPerm = 3
minPerm = 2


grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
percentageRandomFromChosen = 0
percentageAdditionalExtraRandom = 10
minimaalVerschilInVerhoudingImages = 1.1

urlStart = 'https://yandex.com/images/search?text='
urlEnd = '&isize=gt&iw=' + str(minBreedte) +'&ih=' + str(minHoogte)

rawEditorDefaults = RawTherapeeDefaults(".jpg")



screenSizes = [360, 375, 414, 667, 720, 760, 768, 812, 896, 900, 1080, 1366, 1440, 1536, 1920, 1200, 1600, 2560]
const_base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
const_verwijzing_boekhouding_dir = os.path.join(const_base_dir, 'VerwijzingenBoekhouding')
const_model_dir = os.path.join(const_base_dir, 'BesteModellen/inceptionResnetV2_299/m_')
constBenaderde_hash_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_hash.txt')
constBenaderde_url_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_url.txt')
constBenaderde_query_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_woorden.txt')

onderwerpUrlWords = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenOnderwerp.txt'))]
bijvoegelijkeUrlWords = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenBijvoegelijk.txt'))]
bijvoegelijkeUrlWordsEssentie = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenBijvoegelijkEssentie.txt'))]

urlOnderwerpWoordenPermutations = []
for i in range(minPerm, min(len(onderwerpUrlWords) + 1, maxPerm)):
    urlOnderwerpWoordenPermutations.extend(
        ["%20".join(map(str, comb)) for comb in itertools.combinations(onderwerpUrlWords, i)])
urlBijvoegelijkeWoordenPermutations = []
for i in range(minPerm, min(len(bijvoegelijkeUrlWords) + 1, maxPerm)):
    urlBijvoegelijkeWoordenPermutations.extend(
        ["%20".join(map(str, comb)) for comb in itertools.combinations(bijvoegelijkeUrlWords, i)])
urlBijvoegelijkeWoordenEssentiePermutations = []
for i in range(minPerm, min(len(bijvoegelijkeUrlWordsEssentie) + 1, maxPerm)):
    urlBijvoegelijkeWoordenEssentiePermutations.extend(
        ["%20".join(map(str, comb)) for comb in itertools.combinations(bijvoegelijkeUrlWordsEssentie, i)])

urlWoordenPermutaties = [a + '%20' + b + '%20' + c for a in urlBijvoegelijkeWoordenPermutations for b in
                         urlOnderwerpWoordenPermutations for c in urlBijvoegelijkeWoordenEssentiePermutations]
random.shuffle(urlWoordenPermutaties)
print(str(len(urlWoordenPermutaties)) + ' permutaties')

constNieuwePlaatjesLocatie = os.path.join(const_base_dir, 'RawInput')

hash_administratie = readDictFile(constBenaderde_hash_administratie_pad)
url_administratie = readDictFile(constBenaderde_url_administratie_pad)
benaderde_woorden_administratie = readDictFile(constBenaderde_query_administratie_pad)

constClassifier = models.load_model(const_model_dir, custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})
# Testen of hij goed geinitialiseerd is
print(str(classificeer_vollig_image_from_file(os.path.join(const_base_dir, 'maan.jpg'), constClassifier, targetImageSize)))


constBasisWachttijd = 900

options = Options()
regexPlaatje = '(https[^&]+jpg)&'  # '{"url":"([^"]+jpg)"' #{"url":"https://wallpapercave.com/wp/wp6828079.jpg"

vorigeClick = datetime.now() - timedelta(seconds=constBasisWachttijd)

ua = UserAgent()
ua.update()

for woorden_voor_query in urlWoordenPermutaties:
    if woorden_voor_query.replace('%20', ' ') in benaderde_woorden_administratie:
        print(woorden_voor_query.replace('%20', ' ') + ' is al eens bezocht.')
    else:
        zoek_url = urlStart + woorden_voor_query + urlEnd
        print('Zoekterm: ' + woorden_voor_query.replace('%20', ' '))
        queryResultaatScherm = QueryResultaatScherm(query_url=zoek_url)
        gevonden_verwijzingen = queryResultaatScherm.gevonden_verwijzingen_naar_plaatjes
        gevonden_verwijzingen = list(set(gevonden_verwijzingen))
        for url_plaatje in gevonden_verwijzingen:
            url_plaatje = url_plaatje.replace('%3A', ':').replace('%2F', '/')
            if url_plaatje in url_administratie:
                print(url_plaatje + ' is al eens benaderd.')
            else:
                url_administratie[url_plaatje] = str(datetime.now())
                #print(url_plaatje)
                try:
                    img = download_image_naar_memory(url_plaatje)
                except exceptions.InvalidURL as e:
                    print("Url: " + url_plaatje + " niet leesbaar.")
                    print(e)
                    img = None

                if img is None:
                    print(url_plaatje + ' niet gelezen.')
                else:
                    breedte, hoogte = img.size
                    hash_groot = bigHashPicture(img)
                    if hash_groot == '':
                        print(url_plaatje + ' wordt overgeslagen omdat de hash niet klopt')
                    elif hash_groot in hash_administratie:
                        print(url_plaatje + ' al eens gevonden.')
                    elif hoogte < minHoogte or breedte < minBreedte:
                        print(url_plaatje + ' is te klein. Afmetingen: ' + str(img.size))
                    else:
                        hash_administratie[hash_groot] = str(datetime.now())
                        resultaat = classificeer_vollig_image(img, url_plaatje, constClassifier, targetImageSize)
                        keuze = 'niet'
                        if resultaat >= grenswaarde:
                            keuze = 'wel'
                        print(url_plaatje + ' ' + keuze)
                        if keuze == 'wel' or random.random() < resultaat:
                            file_naam = os.path.join(constNieuwePlaatjesLocatie, keuze, hash_groot + ".jpg")
                            sla_image_op(img, file_naam)
                            rawEditorDefaults.maak_specifiek(file_naam, img.size)
                        writeDict(hash_administratie, constBenaderde_hash_administratie_pad)
                writeDict(url_administratie, constBenaderde_url_administratie_pad)
        benaderde_woorden_administratie[woorden_voor_query.replace('%20', ' ')] = datetime.now()
        writeDict(benaderde_woorden_administratie, constBenaderde_query_administratie_pad)
        print('Afgerond ', woorden_voor_query.replace('%20', ' '))
        print("#######################################################################################################################################")

