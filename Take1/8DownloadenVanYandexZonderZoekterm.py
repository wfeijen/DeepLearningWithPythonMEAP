import os
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
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
nogTeLadenNietCounter = 0
aantalWelPerNiet = 1

urlStart = 'https://yandex.com/images'
screenSizes = [360, 375, 414, 667, 720, 760, 768, 812, 896, 900, 1080, 1366, 1440, 1536, 1920, 1200, 1600, 2560]
const_base_dir = '/media/willem/KleindSSD/machineLearningPictures/take1'
const_verwijzing_boekhouding_dir = os.path.join(const_base_dir, 'VerwijzingenBoekhouding')
const_model_dir = os.path.join(const_base_dir, 'BesteModellen/inceptionResnetV2_299/m_')

constBasisWachttijd = 900

options = Options()
regexPlaatje = '(https[^&]+jpg)&'  # '{"url":"([^"]+jpg)"' #{"url":"https://wallpapercave.com/wp/wp6828079.jpg"



plaatjes_beoordelaar = Plaatjes_beoordelaar(model_dir=const_model_dir,
                                            basis_dir=const_base_dir,
                                            nieuwePlaatjesLocatie = os.path.join(const_base_dir, 'RawInput'),
                                            benaderde_hash_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_hash_size.txt'),
                                            benaderde_url_administratie_pad = os.path.join(const_verwijzing_boekhouding_dir, 'benaderde_url.txt'),
                                            minHoogte = minHoogte,
                                            minBreedte = minBreedte,
                                            min_scherpte_grootte = min_scherpte_grootte,
                                            aantalWelPerNiet=aantalWelPerNiet,
                                            grenswaarde = grenswaarde)
vorigeClick = datetime.now() - timedelta(seconds=constBasisWachttijd)
driver = webdriver.Chrome(executable_path="/snap/chromium/current/usr/lib/chromium-browser/chromedriver")
for i in range(100):
    queryResultaatScherm = QueryResultaatScherm(query_url=urlStart, webDriver=driver)
    gevonden_verwijzingen = queryResultaatScherm.gevonden_verwijzingen_naar_plaatjes
    gevonden_verwijzingen = list(set(gevonden_verwijzingen))
    for url_plaatje in gevonden_verwijzingen:
        print("#######################################################################################################################################")
        goed_image, img, file_naam = plaatjes_beoordelaar.laad_en_check_plaatje(url_plaatje = url_plaatje)
        if goed_image:
            plaatjes_beoordelaar.beoordeel_plaatje(img=img, url_plaatje=url_plaatje, file_naam=file_naam)
    print('*******************************************************************************************************************************************')

driver.quit()

