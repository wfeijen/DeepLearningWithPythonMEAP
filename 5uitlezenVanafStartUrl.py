# testsite om uit te lezen: https://vipergirls.to/threads/3226400-InTheCrack-PHOTO-Collection-in-Chronological-Order/page37
# natuurlijk per page uit te lezen

# Doel is een lijst van urls naar voor de hand liggende kandidaten omdat automatisch doorprikken niet altijd mogelijk is.
# Output in de vorm van een html page
# We gaan uit van Vipergirls omdat dat enorm veel content heeft
# Benaming van de file: threadnaam_postnaam (regex voor de postnaam is per tread helaas verschillend)

import requests
import regex
import os
from tensorflow.keras import models
import random
from generiekeFuncties.fileHandlingFunctions import write_na_te_lopen_verwijzingen, readDictFile, writeDict
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image_from_url
from datetime import datetime


grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
percentageRandomFromChosen = 0
percentageAdditionalExtraRandom = 0
minimaalVerschilInVerhoudingImages = 1.1
# url = 'https://vipergirls.to/threads/557628-Vanessa'
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = '<b>([^\~<>]+)\~' #<b>Leggy Bombshell ~
# url = 'https://vipergirls.to/threads/3226400-InTheCrack-PHOTO-Collection-in-Chronological-Order/page37'
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = '<div style="text-align: center;"><font size="5"><b>([^\~<>]+)<' #<div style="text-align: center;"><font size="5"><b>#551 Karlie Montana<
# baseUrl = 'https://vipergirls.to/threads/3262256-Artistic-Nudes-The-Fine-Art-of-Erotica-Rare-Beauty/page'
# volgnummersUrl = range(1, 5)
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = '<font size="3"><div style="text-align: center;"><b>([^\~<>\(]+)\(' #<div style="text-align: center;"><font size="5"><b>#551 Karlie Montana<
baseUrl = 'https://vipergirls.to/threads/3226400-InTheCrack-PHOTO-Collection-in-Chronological-Order/page'
volgnummersUrl = range(120, 125)  # later steeds hoger kan in ieder geval van 100 tot 124
patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
patroon_naam_post = r'<div style="text-align: center;"><font size="5"><b>([^\~<>\(]+)<'  # <div style="text-align: center;"><font size="5"><b>#1629 Maria Rya</b></font><br />
# baseUrl = 'https://vipergirls.to/threads/3262256-Artistic-Nudes-The-Fine-Art-of-Erotica-Rare-Beauty/page'
# volgnummersUrl = range(3, 11)  # 1 - 11
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = r'<font size="3"><div style="text-align: center;"><b>([^\~<>\(]+)\('  # <font size="3"><div style="text-align: center;"><b>Jenna - Tropical Desire (x78)<br />

# Globale variabelen
constPlaatjesEnModelDir = '/mnt/GroteSchijf/machineLearningPictures/take1'
constVerwijzingDir = '/mnt/GroteSchijf/machineLearningPictures/verwijzingen'
constBenaderde_url_administratie_pad = os.path.join(constVerwijzingDir, 'boekhouding/benaderde_urls.txt')
constClassifier = models.load_model(os.path.join(constPlaatjesEnModelDir, 'BesteModellen/besteModelResnetV2'))

benaderde_url_administratie = readDictFile(constBenaderde_url_administratie_pad)

def plunderOverzichtPagina(url, patroon_verwijzing_plaatje, patroon_naam_post):
    randomCounter = 0
    page_text = requests.get(url).text
    posts = page_text.split('<blockquote class="postcontent restore ">')[1:]
    for post in posts:
        urls_for_post = []
        postName = regex.findall(patroon_naam_post, post, regex.IGNORECASE)
        print('Nieuwe Post: ', postName)
        gevonden_verwijzingen = regex.findall(patroon_verwijzing_plaatje, post, regex.IGNORECASE)
        # even de troep er uit
        na_te_lopen_verwijzingen = [(groot, klein) for (groot, klein) in gevonden_verwijzingen if
                                    groot[:4] == 'http' and klein[:4] == 'http']
        if len(postName) > 0:
            postName = postName[0].strip()  # van list naar postname zelf
        else:
            postName = ""
        for na_te_lopen_verwijzing_groot, na_te_lopen_verwijzingen_klein in na_te_lopen_verwijzingen:
            if na_te_lopen_verwijzing_groot not in benaderde_url_administratie:
                randomCounter = randomCounter + random.randint(0, percentageAdditionalExtraRandom * 2)
                resultaat = classificeer_vollig_image_from_url(na_te_lopen_verwijzingen_klein,
                                                               constClassifier,
                                                               targetImageSize)
                if resultaat >= grenswaarde:
                    urls_for_post.append(na_te_lopen_verwijzing_groot)
                    benaderde_url_administratie[na_te_lopen_verwijzing_groot] = str(datetime.now())
                    randomCounter = randomCounter + random.randint(0, percentageRandomFromChosen * 2)
                elif resultaat < 0:
                    print("Verwijzing groot: ", na_te_lopen_verwijzing_groot)
        print('Post ', postName, ' heeft ', len(urls_for_post), ' echte verwijzingen')
        if len(urls_for_post) > 0:
            aantalRandomOpgenomen = 0
            while randomCounter > 0 and len(na_te_lopen_verwijzingen) > 0:
                na_te_lopen_verwijzing = na_te_lopen_verwijzingen[random.randint(0, len(na_te_lopen_verwijzingen) - 1)]
                na_te_lopen_verwijzingen.remove(na_te_lopen_verwijzing)
                na_te_lopen_verwijzing_groot = na_te_lopen_verwijzing[0]
                if na_te_lopen_verwijzing_groot not in benaderde_url_administratie:
                    if na_te_lopen_verwijzing_groot not in urls_for_post:
                        randomCounter = randomCounter - 100
                        urls_for_post.append(na_te_lopen_verwijzing_groot)
                        benaderde_url_administratie[na_te_lopen_verwijzing_groot] = str(datetime.now())
                        aantalRandomOpgenomen = aantalRandomOpgenomen + 1
            print('Post ', postName, ' heeft ', aantalRandomOpgenomen, ' random verwijzingen')
            for key in urls_for_post:
                benaderde_url_administratie[key] = str(datetime.now())
            write_na_te_lopen_verwijzingen(constVerwijzingDir, url, postName, urls_for_post)
            writeDict(benaderde_url_administratie, constBenaderde_url_administratie_pad)


for volgnummerUrl in volgnummersUrl:
    print("#### volgnummer: ", volgnummerUrl)
    url = baseUrl + str(volgnummerUrl)
    plunderOverzichtPagina(url, patroon_verwijzing_plaatje, patroon_naam_post)
