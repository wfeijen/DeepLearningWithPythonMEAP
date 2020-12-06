import time
import regex
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from generiekeFuncties.plaatjesFuncties import download_image_naar_memory, sla_image_op
from generiekeFuncties.fileHandlingFunctions import lees_file_regels_naar_ontdubbelde_lijst, \
    write_lijst_regels_naar_file
from generiekeFuncties.utilities import geeftVoortgangsInformatie, initializeerVoortgangsInformatie
from numpy.random import exponential

# noinspection SpellCheckingInspection
base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
constVerwijzingDir = os.path.join(base_dir, 'Verwijzingen')
constVerwerkteVerwijzingDir = '/mnt/GroteSchijf/machineLearningPictures/take1/Verwerkteverwijzingen'
patroon_verwijzing_plaatje = r'href=\"(https[^\"]*)\" title'
# https://imx.to/i/20bygb

def getActualImageUrlFromImx(driver):
    doc = driver.find_elements_by_xpath('//body/div/span/form/input')
    if len(doc) > 0:
        doc = doc[0]
        doc.click()
        time.sleep(1 + exponential(0.3) + exponential(0.2))
        match = regex.findall(patroon_verwijzing_plaatje, driver.page_source, regex.IGNORECASE)
        if len(match) > 0:
            return (match[0])
    return None


def plaatje_gedownload(url, doelDir, template):
    result = False
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=options)
    browser.minimize_window()
    browser.get(url)
    time.sleep(1 + exponential(0.2) + exponential(0.1))
    # hier strategie bepalen en meegeven
    organisatie = regex.findall('//([^\.]+)\.', url, regex.IGNORECASE)
    if len(organisatie) == 1:
        organisatie = organisatie[0]
        img_url = None
        if organisatie == "imx": img_url = getActualImageUrlFromImx(browser)
        if img_url is not None:
            img = download_image_naar_memory(img_url)
            if img is not None:
                file_name = os.path.join(doelDir, os.path.basename(img_url) + ".jpg")
                sla_image_op(img, file_name)
                breedte, hoogte = img.size
                factor = 16 / 9
                if breedte > hoogte * factor:
                    breedte = hoogte * factor
                else:
                    hoogte = int(breedte / factor)
                inhoud_pp3 = template.replace("teVervangenBreedte",
                                              str(breedte)).replace("teVervangenHoogte",
                                              str(hoogte))
                pp3_file_naam = file_name + ".pp3"
                pp3_file = open(pp3_file_naam, "w")
                pp3_file.write(inhoud_pp3)
                result = True
    browser.quit()
    return result

templateFile = open("rawtherapeeTemplate.pp3")
template = templateFile.read()
templateFile.close()

# webBrowser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
tijdenVorigePunt = initializeerVoortgangsInformatie("start")
opTePakkenVerwijzingDirs = [d for d in os.listdir(constVerwijzingDir)
                            if os.path.isdir(os.path.join(constVerwijzingDir, d))]
for verwijzingsDir in opTePakkenVerwijzingDirs:
    verwijzingsFile = os.path.join(constVerwijzingDir, verwijzingsDir, "verwijzingen.txt")
    lijstMislukteUrls = []
    verwijzingen = lees_file_regels_naar_ontdubbelde_lijst(verwijzingsFile)
    tijdenVorigePunt = geeftVoortgangsInformatie("VerwijzingsDir: " + verwijzingsDir + " met " + str(len(verwijzingen)) + " verwijzingen. ", tijdenVorigePunt)
    for verwijzing in verwijzingen:
        if not plaatje_gedownload(verwijzing, os.path.join(constVerwijzingDir, verwijzingsDir), template):
            lijstMislukteUrls.append(verwijzing)
            print(verwijzing, " mislukt")
        else:
            print(verwijzing)
    if len(lijstMislukteUrls) > 0:
        write_lijst_regels_naar_file(os.path.join(constVerwijzingDir, verwijzingsDir, "foutGegaan.txt"), lijstMislukteUrls)
    else:
        shutil.move(os.path.join(constVerwijzingDir, verwijzingsDir),
                    os.path.join(constVerwerkteVerwijzingDir, verwijzingsDir))

