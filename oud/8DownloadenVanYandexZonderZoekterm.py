import os
from tensorflow.keras import models
from generiekeFuncties.fileHandlingFunctions import readDictFile, writeDict, lees_file_regels_naar_ontdubbelde_lijst, dict_values_string_to_int
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, download_image_naar_memory, sla_image_op, bigHashPicture, scherpte_maalGrootte_image
from datetime import datetime, timedelta
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m
from selenium.webdriver.chrome.options import Options
from requests import exceptions
from generiekeFuncties.queryResultaatScherm import QueryResultaatScherm
from selenium import webdriver
from generiekeFuncties.plaatjes_downloader_en_beoordeler import Plaatjes_beoordelaar


# &isize=gt&iw=999&ih=1199
# https://yandex.com/tune/


minBreedte = 999
minHoogte = 1199
minFileSize = 100 #kB
min_scherpte_grootte = 2000


grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
nogTeLadenNietCounter = 0
aantalWelPerNiet = 1

urlStart = 'https://yandex.com/images'




screenSizes = [360, 375, 414, 667, 720, 760, 768, 812, 896, 900, 1080, 1366, 1440, 1536, 1920, 1200, 1600, 2560]
const_base_dir = '/media/willem/KleindSSD/machineLearningPictures/take1'
const_verwijzing_boekhouding_dir = os.path.join(const_base_dir, 'VerwijzingenBoekhouding')
const_model_dir = os.path.join(const_base_dir, 'BesteModellen/inceptionResnetV2_299/m_')
constBenaderde_hash_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_hash_size.txt')
constBenaderde_url_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_url.txt')
constBenaderde_query_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_woorden.txt')

onderwerpUrlWords = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenOnderwerp.txt'))]
bijvoegelijkeUrlWords = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenBijvoegelijk.txt'))]
bijvoegelijkeUrlWordsEssentie = [woorden.replace(' ', '%20') for woorden in lees_file_regels_naar_ontdubbelde_lijst(
    os.path.join(const_verwijzing_boekhouding_dir, 'woordenBijvoegelijkEssentie.txt'))]

# ua = UserAgent()
# ua.update()


constNieuwePlaatjesLocatie = os.path.join(const_base_dir, 'RawInput')

hash_administratie = readDictFile(constBenaderde_hash_administratie_pad)
hash_administratie = dict_values_string_to_int(hash_administratie)
url_administratie = readDictFile(constBenaderde_url_administratie_pad)
benaderde_woorden_administratie = readDictFile(constBenaderde_query_administratie_pad)

constClassifier = models.load_model(const_model_dir, custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})
# Testen of hij goed geinitialiseerd is
print(str(classificeer_vollig_image_from_file(os.path.join(const_base_dir, 'maan.jpg'), constClassifier, targetImageSize)))


constBasisWachttijd = 900

options = Options()
regexPlaatje = '(https[^&]+jpg)&'  # '{"url":"([^"]+jpg)"' #{"url":"https://wallpapercave.com/wp/wp6828079.jpg"

vorigeClick = datetime.now() - timedelta(seconds=constBasisWachttijd)
driver = webdriver.Chrome(executable_path="/snap/chromium/current/usr/lib/chromium-browser/chromedriver")

plaatjes_beoordelaar = Plaatjes_beoordelaar

for i in range(100):
    zoek_url = urlStart
    queryResultaatScherm = QueryResultaatScherm(query_url=zoek_url, webDriver=driver)
    gevonden_verwijzingen = queryResultaatScherm.gevonden_verwijzingen_naar_plaatjes
    gevonden_verwijzingen = list(set(gevonden_verwijzingen))
    for url_plaatje in gevonden_verwijzingen:
        goed_image = False
        url_plaatje = url_plaatje.replace('%3A', ':').replace('%2F', '/')
        print(url_plaatje)
        if url_plaatje in url_administratie:
            print('   is al eens benaderd.')
        else:
            url_administratie[url_plaatje] = str(datetime.now())
            try:
                img = download_image_naar_memory(url_plaatje)
            except exceptions.InvalidURL as e:
                print("   niet leesbaar.")
                print(e)
                img = None

            if img is None:
                print('   niet gelezen.')
            else:
                breedte, hoogte = img.size
                scherpte = scherpte_maalGrootte_image(im = img)
                print('s: ' + str(scherpte) + ' b: ' + breedte + ' h: ' + hoogte)
                hash_groot = bigHashPicture(img)
                if hash_groot == '':
                    print('   wordt overgeslagen omdat de hash niet klopt')
                elif hoogte < minHoogte or breedte < minBreedte:
                    print('   is te klein.')
                elif scherpte < min_scherpte_grootte:
                    print('   scherpte grootte onvoldoende')
                elif hash_groot in hash_administratie:
                    if hash_administratie[hash_groot] >= scherpte:
                        print('   al eens gevonden.')
                    else:
                        print('   verbeterde scherpte maal grootte')
                        goed_image = True
                else:
                    goed_image = True

                if goed_image:
                    hash_administratie[hash_groot] = scherpte
                    resultaat = classificeer_vollig_image(img, url_plaatje, constClassifier, targetImageSize)
                    if resultaat >= grenswaarde:
                        keuze = 'wel'
                        nogTeLadenNietCounter += 1
                    else:
                        keuze = 'niet'
                        nietPlaatjeLaden = nogTeLadenNietCounter >= aantalWelPerNiet
                        if nietPlaatjeLaden:
                            nogTeLadenNietCounter = nogTeLadenNietCounter - aantalWelPerNiet
                    print('     ' + keuze)
                    if keuze == 'wel' or nietPlaatjeLaden:
                        file_naam = os.path.join(constNieuwePlaatjesLocatie, keuze, hash_groot + ".jpg")
                        print(file_naam)
                        sla_image_op(img, file_naam)
                    writeDict(hash_administratie, constBenaderde_hash_administratie_pad)
            writeDict(url_administratie, constBenaderde_url_administratie_pad)
        print("#######################################################################################################################################")

driver.quit()

