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

grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
percentageRandomFromChosen = 0
percentageAdditionalExtraRandom = 10
minimaalVerschilInVerhoudingImages = 1.1

urlStart = 'https://yandex.com/images/search?text='
urlEnd = '&isize=gt&iw=1920&ih=1080&recent=8D&p='
urlWords = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst('./data/woorden.txt')]

urlWordPermutations = []
for i in range(2, len(urlWords)+1):
    urlWordPermutations.extend(["%20".join(map(str, comb)) for comb in itertools.combinations(urlWords, i)])

screenSizes = [360, 375, 414, 667, 720, 760, 768, 812, 896, 900, 1080, 1366, 1440, 1536, 1920, 1200, 1600, 2560]
base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
modelPath = os.path.join(base_dir, 'BesteModellen/m_')
constBenaderde_hash_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_hash.txt')
constBenaderde_url_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_url.txt')
constBenaderde_query_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_query.txt')

constNieuwePlaatjesLocatie = os.path.join(base_dir, 'RawInput')

hash_administratie = readDictFile(constBenaderde_hash_administratie_pad)
url_administratie = readDictFile(constBenaderde_url_administratie_pad)
query_administratie = readDictFile(constBenaderde_query_administratie_pad)

constClassifier = models.load_model(modelPath, custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})
# Testen of hij goed geinitialiseerd is
print(str(classificeer_vollig_image_from_file('./data/maan.jpg', constClassifier, targetImageSize)))


constBasisWachttijd = 900

options = Options()
regexPlaatje = '(https[^&]+jpg)&'  # '{"url":"([^"]+jpg)"' #{"url":"https://wallpapercave.com/wp/wp6828079.jpg"

vorigeClick = datetime.now() - timedelta(seconds=constBasisWachttijd)


def haal_query_resultaat_op(query_url, tijd_vorige_query):
    user_agent = UserAgent().random
    print(user_agent)
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options,
                              executable_path="/usr/lib/chromium-browser/chromedriver")
#        driver.set_window_size(random.choice(screenSizes), random.choice(screenSizes))
    driver.minimize_window()
    nog_wachten = max(0.0, constBasisWachttijd - (datetime.now() - tijd_vorige_query).total_seconds()) + exponential(0.3) + exponential(0.2)
    print(query_url)
    print('start wachten: ' + str(datetime.now()) + ' nog wachten: ' + str(nog_wachten))
    time.sleep(nog_wachten)
    print('Klaar met wachten: ' + str(datetime.now()))
    driver.get(query_url)
    tijd_vorige_query = datetime.now()

    # driver.click()
    page_query_resultaat = driver.page_source
    driver.quit()
# Voor debug doeleinden schrijven we de pagina weg
    f = open('data/pageSave' + str(datetime.now()) + '.html', 'w')
    f.write(page_query_resultaat)
    f.close()
    return page_query_resultaat, tijd_vorige_query


for woorden_voor_query in urlWordPermutations:
    i = 1
    einde = False
    while not einde:
        zoek_url = urlStart + woorden_voor_query + urlEnd + str(i)
        print('Zoekterm: ' + woorden_voor_query)
        if zoek_url in query_administratie:
            print(zoek_url + ' is al eens bezocht.')
        else:
            page_text, vorigeClick = haal_query_resultaat_op(query_url=zoek_url, tijd_vorige_query=vorigeClick)
            # Zoeken naar plaatjes voorbeeld: {"url":"https://wallpapercave.com/wp/wp6828079.jpg"
            gevonden_verwijzingen = regex.findall(regexPlaatje, page_text, regex.IGNORECASE)
            if len(gevonden_verwijzingen) == 0:
                print('Niks gevonden. Hier zijn we klaar.')
                einde = True
            else:
                for url_plaatje in gevonden_verwijzingen:
                    url_plaatje = url_plaatje.replace('%3A', ':').replace('%2F', '/')
                    if url_plaatje in url_administratie:
                        print(url_plaatje + ' is al eens benaderd.')
                    else:
                        url_administratie[url_plaatje] = str(datetime.now())
                        print(url_plaatje)
                        img = download_image_naar_memory(url_plaatje)
                        if img is None:
                            print(url_plaatje + ' niet gelezen.')
                        else:
                            hash_groot = bigHashPicture(img)
                            if hash_groot == '':
                                print(url_plaatje + ' wordt overgeslagen omdat de hash niet klopt')
                            elif hash_groot in hash_administratie:
                                print(url_plaatje + ' al eens gevonden.')
                            elif max(img.size) < 1000:
                                print(url_plaatje + ' is te klein. Afmetingen: ' + str(img.size))
                            else:
                                hash_administratie[hash_groot] = str(datetime.now())
                                resultaat = classificeer_vollig_image(img, url_plaatje, constClassifier, targetImageSize)
                                keuze = 'niet'
                                if resultaat >= grenswaarde:
                                    keuze = 'wel'
                                sla_image_op(img, os.path.join(constNieuwePlaatjesLocatie, keuze, hash_groot + ".jpg"))
                                writeDict(hash_administratie, constBenaderde_hash_administratie_pad)
                        writeDict(url_administratie, constBenaderde_url_administratie_pad)
                query_administratie[zoek_url] = datetime.now()
                writeDict(query_administratie, constBenaderde_query_administratie_pad)
        i += 1
