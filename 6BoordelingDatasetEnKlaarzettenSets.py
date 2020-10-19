import os
from generiekeFuncties.fileHandlingFunctions import give_list_of_images, readDictFile, \
    write_na_te_lopen_verwijzingen_directorie, silentremove, verwijderGecontroleerdeFilesBovenNummerFromList
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.plaatjesFuncties import bigHash_size

directoryNr = 2
aantal = 25
hash_size = bigHash_size()

onderzoeks_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/rawInput'
constVerwijzingDir = '/mnt/GroteSchijf/machineLearningPictures/verwijzingen'
constWelDir = os.path.join(onderzoeks_dir, "wel")
constNietDir = os.path.join(onderzoeks_dir, "niet")

imageList_P = [os.path.join(constWelDir, fileName) for fileName in
               give_list_of_images(subdirName="wel", baseDir=onderzoeks_dir)]
imageList_P.sort()
imageList_geen_P = [os.path.join(constNietDir, fileName) for fileName in
                    give_list_of_images(subdirName="niet", baseDir=onderzoeks_dir)]
imageList_geen_P.sort()

imageList_P = verwijderGecontroleerdeFilesBovenNummerFromList(imageList_P, 1)
imageList_geen_P = verwijderGecontroleerdeFilesBovenNummerFromList(imageList_geen_P, 1)

Viewer(imgList=imageList_geen_P, titel="NIET", aanleidingTotVeranderen="wel")

Viewer(imgList=imageList_P, titel="WEL", aanleidingTotVeranderen="niet")

# Testen of er nog files niet gecontroleerd zijn
lijst_niet_gecontroleerd = [f for f in os.listdir(constWelDir) if "gecontroleerd" not in f]
lijst_niet_gecontroleerd.extend([f for f in os.listdir(constNietDir) if "gecontroleerd" not in f])

if len(lijst_niet_gecontroleerd) == 0:
    voorbereidingVerwijzingenLijst = [os.path.join(constVerwijzingDir, f) for f in os.listdir(constVerwijzingDir)
                                      if os.path.isfile(os.path.join(constVerwijzingDir, f))]
    welHashes = [f[: hash_size * 4] for f in os.listdir(constWelDir)]

    for voorbereiding_verwijzingen_file in voorbereidingVerwijzingenLijst:
        hashes_en_verwijzingen = readDictFile(voorbereiding_verwijzingen_file)
        verwijzing_lijst = []
        for hash, verwijzing in hashes_en_verwijzingen.items():
            # Zoek of hij in wel of niet zit
            if hash in welHashes:
                verwijzing_lijst.append(verwijzing)
        if len(verwijzing_lijst) > 0:
            # Filenaam omzetten naar dirnaam door .txt er af te laten vallen
            dir_naam = voorbereiding_verwijzingen_file[:-4]
            write_na_te_lopen_verwijzingen_directorie(dir_naam, verwijzing_lijst)
        silentremove(voorbereiding_verwijzingen_file)
    print("lijsten klaargezet")






