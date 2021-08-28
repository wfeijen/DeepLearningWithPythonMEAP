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
from generiekeFuncties.fileHandlingFunctions import write_voorbereiding_na_te_lopen_verwijzingen, readDictFile, writeDict
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image, download_image_naar_memory, sla_image_op, bigHashPicture
from datetime import datetime
from generiekeFuncties.utilities import initializeerVoortgangsInformatie, geeftVoortgangsInformatie
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m

grenswaarde = 0.5  # Waarde waarboven we uitgaan van een p plaatje
targetImageSize = get_target_picture_size()
percentageRandomFromChosen = 0
percentageAdditionalExtraRandom = 10
minimaalVerschilInVerhoudingImages = 1.1


###########################################################################################
baseUrl = 'https://vipergirls.to/threads/3545152-MetArt-2018-High-Resolution!/page'
volgnummersUrl = range(31, 41)  #   1 - 46
patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
patroon_naam_post = r'([0-9]{4}-[0-9]{2}-[0-9]{2}[^\<]+)<'  # 2019-06-19 - Monika Dee - Time To Unwind<br />


# Globale variabelen
base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
modelPath = os.path.join(base_dir, 'BesteModellen/inceptionResnetV2_299/m_')
constVoorberVerwijzingDir = os.path.join(base_dir, 'Verwijzingen')
constBenaderde_hash_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_hash.txt')
constNieuwePlaatjesLocatie = os.path.join(base_dir, 'RawInput')
constClassifier = models.load_model(modelPath,
                               custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})

hash_administratie = readDictFile(constBenaderde_hash_administratie_pad)

def plunder_overzicht_pagina(url_in, patroon_verwijzing_plaatje_in, patroon_naam_post_in, vgi):
    random_counter = 0
    page_text = requests.get(url_in).text
    posts = page_text.split('<blockquote class="postcontent restore ">')[1:]
    for post in posts:
        hashes_voor_lokale_filenaam_en_url_groot = {}
        postname = regex.findall(patroon_naam_post_in, post, regex.IGNORECASE)
        gevonden_verwijzingen = regex.findall(patroon_verwijzing_plaatje_in, post, regex.IGNORECASE)
        if len(postname) > 0:
            postname = postname[0].strip()  # van list naar postname zelf
        else:
            postname = ""
        # even de troep er uit
        na_te_lopen_verwijzingen = [(groot, klein) for (groot, klein) in gevonden_verwijzingen if
                                    groot[:4] == 'http' and klein[:4] == 'http']
        vgi = geeftVoortgangsInformatie(
            'Post ' + postname + ' met ' + str(len(na_te_lopen_verwijzingen)) + ' gevonden verwijzingen',
            vgi)
        for na_te_lopen_verwijzing_groot, na_te_lopen_verwijzing_klein in na_te_lopen_verwijzingen:
            random_counter = random_counter + percentageAdditionalExtraRandom #random.randint(0, percentageAdditionalExtraRandom * 2)
            if na_te_lopen_verwijzing_groot not in na_te_lopen_verwijzingen:
                img = download_image_naar_memory(na_te_lopen_verwijzing_klein)
                if img is None:
                    resultaat = -1
                else:
                    hash_groot = bigHashPicture(img)
                    if hash_groot not in hash_administratie:
                        resultaat = classificeer_vollig_image(img, na_te_lopen_verwijzing_klein,
                                                                       constClassifier,
                                                                       targetImageSize)
                        if resultaat >= grenswaarde:
                            hashes_voor_lokale_filenaam_en_url_groot[hash_groot] = na_te_lopen_verwijzing_groot
                            hash_administratie[hash_groot] = str(datetime.now())
                            random_counter = random_counter + percentageRandomFromChosen #random.randint(0, percentageRandomFromChosen * 2)
                            sla_image_op(img, os.path.join(constNieuwePlaatjesLocatie, "wel", hash_groot + ".jpg"))
                        elif resultaat < 0:
                            print("Negatieve score: ", na_te_lopen_verwijzing_groot)
        vgi = geeftVoortgangsInformatie(
            'Post ' + postname + ' heeft ' + str(len(hashes_voor_lokale_filenaam_en_url_groot)) + ' echte verwijzingen',
            vgi)
        aantalRandomOpgenomen = 0
        while random_counter > 0 and len(na_te_lopen_verwijzingen) > 0:
            na_te_lopen_verwijzing = na_te_lopen_verwijzingen[random.randint(0, len(na_te_lopen_verwijzingen) - 1)]
            na_te_lopen_verwijzingen.remove(na_te_lopen_verwijzing)
            na_te_lopen_verwijzing_groot, na_te_lopen_verwijzing_klein = na_te_lopen_verwijzing
            img = download_image_naar_memory(na_te_lopen_verwijzing_klein)
            if img is not None:
                hash_groot = bigHashPicture(img)
                if hash_groot not in hash_administratie:
                    if na_te_lopen_verwijzing_groot not in hashes_voor_lokale_filenaam_en_url_groot:
                        random_counter = random_counter - 100
                        hash_administratie[hash_groot] = str(datetime.now())
                        sla_image_op(img, os.path.join(constNieuwePlaatjesLocatie, "niet", hash_groot + ".jpg"))
                        hashes_voor_lokale_filenaam_en_url_groot[hash_groot] = na_te_lopen_verwijzing_groot
                        aantalRandomOpgenomen = aantalRandomOpgenomen + 1
        vgi = geeftVoortgangsInformatie(
            'Post ' + postname + ' heeft ' + str(aantalRandomOpgenomen) + ' random verwijzingen'
            , vgi)

        write_voorbereiding_na_te_lopen_verwijzingen(constVoorberVerwijzingDir, url_in, postname, hashes_voor_lokale_filenaam_en_url_groot)
        writeDict(hash_administratie, constBenaderde_hash_administratie_pad)


voortgangs_informatie = initializeerVoortgangsInformatie("Uitlezen urls")
for volgnummerUrl in volgnummersUrl:
    voortgangs_informatie = geeftVoortgangsInformatie("#### volgnummer: " + str(volgnummerUrl), voortgangs_informatie)
    url = baseUrl + str(volgnummerUrl)
    plunder_overzicht_pagina(url, patroon_verwijzing_plaatje, patroon_naam_post, voortgangs_informatie)


#################################### nog doen
# https://vipergirls.to/threads/103533-Watch4Beauty/page67
# https://vipergirls.to/threads/1633619-Met-amp-Fem-gt-gt-gt-Nude-Erotic-Model-Collection-lt-lt-lt-2014-2015/page8
# https://vipergirls.to/threads/602689-All-Sexy-Shaved-Danish-Amateur-Models-(Collection)/page18
# https://vipergirls.to/threads/600140-Artistic-gt-gt-Tasteful-gt-gt-Nude-gt-gt-Erotic-gt-gt-Full-Sets-gt-gt-gt-(Collection)/page79
# https://vipergirls.to/threads/624686-NextDoor-Models-Various-Sets/page2
# https://vipergirls.to/threads/2156553-Twistys-lt-lt-lt-lt-Shaved-Pretty-Pornstars-amp-Nude-Babes-lt-lt-lt-Solo-Full-Sets-gt-gt-gt-(Collection)-Alphabetic/page10
# https://vipergirls.to/threads/2809525-ATK-Natural-Hairy-Felix/page7
# https://vipergirls.to/threads/3663081-Artistic-Nude-2017-amp-2018-20-Beautiful-Site-Updates-High-Resolution-File-Archive-NEW/page4
# https://vipergirls.to/threads/3539087-(((-MetArt-)))-2017-amp-2018-High-Resolution-File-Archive-NEW/page15
#
##################################### Zonder namen
# https://vipergirls.to/threads/1267445-Mature-MILF-sofcore-amp-hardcore-images-collection/page8
# https://vipergirls.to/threads/661683-ITC-Best-of-pose-for-close-ups-PornStars-(Collection-amp-Updates)/page2
# https://vipergirls.to/threads/644877-66Models-(-The-Best-of-Collection-amp-Updates-2014-)-NEW/page4

#################################### Al gedaan en voorbeelden
# baseUrl = 'https://vipergirls.to/threads/3226400-InTheCrack-PHOTO-Collection-in-Chronological-Order/page'
# volgnummersUrl = range(125, 126)  # later steeds hoger kan in ieder geval van 100 tot 124
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = r'<div style="text-align: center;"><font size="5"><b>([^\~<>\(]+)<'  # <div style="text-align: center;"><font size="5"><b>#1629 Maria Rya</b></font><br />
# baseUrl = 'https://vipergirls.to/threads/3262256-Artistic-Nudes-The-Fine-Art-of-Erotica-Rare-Beauty/page'
# volgnummersUrl = range(11, 12)  # 1 - 11
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = r'<font size="3"><div style="text-align: center;"><b>([^\~<>\(]+)\('  # <font size="3"><div style="text-align: center;"><b>Jenna - Tropical Desire (x78)<br />
# baseUrl = 'https://vipergirls.to/threads/4371605-Ruthless-Mistress-Femdom/page'
# volgnummersUrl = range(1, 147)  # 1 - 146
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = r'([^<]+)<br />'  # <h2 class="title icon">\nMia Li is Gia Dimarco's Hot Lesbian Foot Toy\n</h2>
# url = 'https://vipergirls.to/threads/557628-Vanessa/page1-13'
# baseUrl = 'https://vipergirls.to/threads/3262256-Artistic-Nudes-The-Fine-Art-of-Erotica-Rare-Beauty/page'
# volgnummersUrl = range(2, 14)
# patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
# patroon_naam_post = '<b>([^\~<>]+)\~' #<b>Leggy Bombshell ~
###########################################################################################
baseUrl = 'https://vipergirls.to/threads/4254377-MetArt-2019-High-Resolution!/page'
volgnummersUrl = range(51, 61)  #   1 - 46
patroon_verwijzing_plaatje = r'<a href=\"([^\"]+)\"[^>]+><img src=\"([^\"]+)\"[^>]+>'
patroon_naam_post = r'([^<]+)<br />'  # 2019-06-19 - Monika Dee - Time To Unwind<br />