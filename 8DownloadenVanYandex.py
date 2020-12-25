import requests
import regex
import os
from tensorflow.keras import models
import random
from generiekeFuncties.fileHandlingFunctions import write_voorbereiding_na_te_lopen_verwijzingen, readDictFile, writeDict
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image, download_image_naar_memory, sla_image_op, bigHashPicture, classificeer_vollig_image_from_file
from datetime import datetime, timedelta
from generiekeFuncties.utilities import initializeerVoortgangsInformatie, geeftVoortgangsInformatie
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m
import itertools
import time
from numpy.random import exponential

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
percentageRandomFromChosen = 0
percentageAdditionalExtraRandom = 10
minimaalVerschilInVerhoudingImages = 1.1

urlStart = 'https://yandex.com/images/search?text='
urlEnd = '&isize=gt&iw=1920&ih=1080&recent=8D&p='
urlWords = ["cum", "dripping", "pussy", "creampy", "clean"]

screenSizes = [360, 375, 414, 667, 720, 760, 768, 812, 896, 900, 1080, 1366, 1440, 1536, 1920, 1200, 1600, 2560]
base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
modelPath = os.path.join(base_dir, 'BesteModellen/m_')
constBenaderde_hash_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_hash.txt')
constBenaderde_url_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_url.txt')

constNieuwePlaatjesLocatie = os.path.join(base_dir, 'RawInput')

hash_administratie = readDictFile(constBenaderde_hash_administratie_pad)
url_administratie = readDictFile(constBenaderde_url_administratie_pad)

constClassifier = models.load_model(modelPath, custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})
# Testen of hij goed geinitialiseerd is
print(str(classificeer_vollig_image_from_file('./data/maan.jpg', constClassifier, targetImageSize)))


constBasisWachttijd = 300

options = Options()
ua = UserAgent()
regexPlaatje = '(https[^&]+jpg)&' #'{"url":"([^"]+jpg)"' #{"url":"https://wallpapercave.com/wp/wp6828079.jpg"
urlWordPermutations = list.copy(urlWords)
for i in range(2, len(urlWords)+1):
    urlWordPermutations.extend(["%20".join(map(str, comb)) for comb in itertools.combinations(urlWords, i)])

vorigeClick = datetime.now() - timedelta(seconds=constBasisWachttijd)

for urlWordPermutation in urlWordPermutations:
    i = 1
    einde = False
    while not einde:
        userAgent = ua.random
        print(userAgent)
        options.add_argument(f'user-agent={userAgent}')
        driver = webdriver.Chrome(chrome_options=options,
                                  executable_path="/usr/lib/chromium-browser/chromedriver")
        driver.set_window_size(random.choice(screenSizes), random.choice(screenSizes))
        driver.minimize_window()
        zoekUrl = urlStart + urlWordPermutation + urlEnd #+ str(i)
        nog_wachten = max(0, constBasisWachttijd - (datetime.now() - vorigeClick).total_seconds())
        time.sleep(nog_wachten + exponential(0.3) + exponential(0.2))
        driver.get(zoekUrl)
        vorigeClick = datetime.now()

        # driver.click()
        page_text = driver.page_source
        driver.quit()
    # Voor debug doeleinden schrijven we de pagina weg
        f = open('data/pageSave' + str(datetime.now()) + '.html', 'w')
        f.write(page_text)
        f.close()


        # Zoeken naar plaatjes voorbeeld: {"url":"https://wallpapercave.com/wp/wp6828079.jpg"
        gevonden_verwijzingen = regex.findall(regexPlaatje, page_text, regex.IGNORECASE)
        if len(gevonden_verwijzingen) == 0:
            einde = True
        else:
            i += i
            for url_plaatje in gevonden_verwijzingen:
                if url_plaatje not in url_administratie:
                    url_plaatje = url_plaatje.replace('%3A', ':').replace('%2F', '/')
                    url_administratie[url_plaatje] = str(datetime.now())
                    print(url_plaatje)
                    img = download_image_naar_memory(url_plaatje)
                    hash_groot = bigHashPicture(img)
                    if hash_groot not in hash_administratie:
                        hash_administratie[hash_groot] = str(datetime.now())
                        resultaat = classificeer_vollig_image(img, url_plaatje, constClassifier, targetImageSize)
                        keuze = 'niet'
                        if resultaat >= grenswaarde:
                            keuze = 'wel'
                        sla_image_op(img, os.path.join(constNieuwePlaatjesLocatie, keuze, hash_groot + ".jpg"))

