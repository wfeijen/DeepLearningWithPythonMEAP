# testsite om uit te lezen: https://vipergirls.to/threads/3226400-InTheCrack-PHOTO-Collection-in-Chronological-Order/page37
# natuurlijk per page uit te lezen

# Doel is een lijst van urls naar voor de hand liggende kandidaten omdat automatisch doorprikken niet altijd mogelijk is.
# Output in de vorm van een html page
# We gaan uit van Vipergirls omdat dat enorm veel content heeft
# Benaming van de file: threadnaam_postnaam (regex voor de postnaam is per tread helaas verschillend)

# Urls blijken vergankelijk Dus op hash. 16 cijfers


import requests
import regex
import os
from tensorflow.keras import models
import random
from generiekeFuncties.fileHandlingFunctions import write_na_te_lopen_verwijzingen, readDictFile, writeDict
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image, download_image_naar_memory, sla_image_op, bigHashPicture
from datetime import datetime


grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
percentageRandomFromChosen = 5
percentageAdditionalExtraRandom = 5
minimaalVerschilInVerhoudingImages = 1.1
# url = 'https://vipergirls.to/threads/557628-Vanessa/page1-13'
# baseUrl = 'https://vipergirls.to/threads/3262256-Artistic-Nudes-The-Fine-Art-of-Erotica-Rare-Beauty/page'
# volgnummersUrl = range(2, 14)
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = '<b>([^\~<>]+)\~' #<b>Leggy Bombshell ~


# baseUrl = 'https://vipergirls.to/threads/3262256-Artistic-Nudes-The-Fine-Art-of-Erotica-Rare-Beauty/page'
# volgnummersUrl = range(5,6)
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = '<font size="3"><div style="text-align: center;"><b>([^\~<>\(]+)\(' #<div style="text-align: center;"><font size="5"><b>#551 Karlie Montana<
baseUrl = 'https://vipergirls.to/threads/3226400-InTheCrack-PHOTO-Collection-in-Chronological-Order/page'
volgnummersUrl = range(125, 126)  # later steeds hoger kan in ieder geval van 100 tot 124
patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
patroon_naam_post = r'<div style="text-align: center;"><font size="5"><b>([^\~<>\(]+)<'  # <div style="text-align: center;"><font size="5"><b>#1629 Maria Rya</b></font><br />
# baseUrl = 'https://vipergirls.to/threads/3262256-Artistic-Nudes-The-Fine-Art-of-Erotica-Rare-Beauty/page'
# volgnummersUrl = range(3, 11)  # 1 - 11
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = r'<font size="3"><div style="text-align: center;"><b>([^\~<>\(]+)\('  # <font size="3"><div style="text-align: center;"><b>Jenna - Tropical Desire (x78)<br />

# Globale variabelen
constPlaatjesEnModelDir = '/mnt/GroteSchijf/machineLearningPictures/take1'
constVerwijzingDir = '/mnt/GroteSchijf/machineLearningPictures/verwijzingen'
constBenaderde_url_administratie_pad = '/mnt/GroteSchijf/machineLearningPictures/verwijzingenBoekhouding/benaderde_hash.txt'
constNieuwePlaatjesLocatie = '/mnt/GroteSchijf/machineLearningPictures/take1/rawInput'
constClassifier = models.load_model(os.path.join(constPlaatjesEnModelDir, 'BesteModellen/besteModelResnetV2'))

hash_administratie = readDictFile(constBenaderde_url_administratie_pad)

def plunder_overzicht_pagina(url_in, patroon_verwijzing_plaatje_in, patroon_naam_post_in):
    random_counter = 0
    page_text = requests.get(url_in).text
    posts = page_text.split('<blockquote class="postcontent restore ">')[1:]
    for post in posts:
        urls_for_post = []
        postname = regex.findall(patroon_naam_post_in, post, regex.IGNORECASE)
        print('Nieuwe Post: ', postname)
        gevonden_verwijzingen = regex.findall(patroon_verwijzing_plaatje_in, post, regex.IGNORECASE)
        # even de troep er uit
        na_te_lopen_verwijzingen = [(groot, klein) for (groot, klein) in gevonden_verwijzingen if
                                    groot[:4] == 'http' and klein[:4] == 'http']
        if len(postname) > 0:
            postname = postname[0].strip()  # van list naar postname zelf
        else:
            postname = ""
        for na_te_lopen_verwijzing_groot, na_te_lopen_verwijzingen_klein in na_te_lopen_verwijzingen:
            random_counter = random_counter + random.randint(0, percentageAdditionalExtraRandom * 2)
            img = download_image_naar_memory(na_te_lopen_verwijzingen_klein)
            if img is None:
                resultaat = -1
            else:
                hash = bigHashPicture(img)
                if hash not in hash_administratie:
                    resultaat = classificeer_vollig_image(img, na_te_lopen_verwijzingen_klein,
                                                                   constClassifier,
                                                                   targetImageSize)
                    if resultaat >= grenswaarde:
                        urls_for_post.append(na_te_lopen_verwijzing_groot)
                        hash_administratie[hash] = str(datetime.now())
                        random_counter = random_counter + random.randint(0, percentageRandomFromChosen * 2)
                        sla_image_op(img, os.path.join(constNieuwePlaatjesLocatie, "wel", hash + ".jpg"))
                    elif resultaat < 0:
                        print("Verwijzing groot: ", na_te_lopen_verwijzing_groot)
        print('Post ', postname, ' heeft ', len(urls_for_post), ' echte verwijzingen')
        if len(urls_for_post) > 0:
            aantalRandomOpgenomen = 0
            while random_counter > 0 and len(na_te_lopen_verwijzingen) > 0:
                na_te_lopen_verwijzing = na_te_lopen_verwijzingen[random.randint(0, len(na_te_lopen_verwijzingen) - 1)]
                na_te_lopen_verwijzingen.remove(na_te_lopen_verwijzing)
                na_te_lopen_verwijzing_groot, na_te_lopen_verwijzing_klein = na_te_lopen_verwijzing
                img = download_image_naar_memory(na_te_lopen_verwijzingen_klein)
                hash = bigHashPicture(img)
                if hash not in hash_administratie:
                    if na_te_lopen_verwijzing_groot not in urls_for_post:
                        random_counter = random_counter - 100
                        urls_for_post.append(na_te_lopen_verwijzing_groot)
                        hash_administratie[hash] = str(datetime.now())
                        sla_image_op(img, os.path.join(constNieuwePlaatjesLocatie, "niet", hash + ".jpg"))
                        aantalRandomOpgenomen = aantalRandomOpgenomen + 1
            print('Post ', postname, ' heeft ', aantalRandomOpgenomen, ' random verwijzingen')
            for key in urls_for_post:
                hash_administratie[key] = str(datetime.now())
            write_na_te_lopen_verwijzingen(constVerwijzingDir, url_in, postname, urls_for_post)
            writeDict(hash_administratie, constBenaderde_url_administratie_pad)


for volgnummerUrl in volgnummersUrl:
    print("#### volgnummer: ", volgnummerUrl)
    url = baseUrl + str(volgnummerUrl)
    plunder_overzicht_pagina(url, patroon_verwijzing_plaatje, patroon_naam_post)
