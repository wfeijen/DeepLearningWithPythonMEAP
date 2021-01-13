import os
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir, readDictFile, \
    write_na_te_lopen_verwijzingen_directorie, silentremove
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.plaatjesFuncties import bigHash_size

directoryNr = 2
aantal = 25
hash_size = bigHash_size()

base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
onderzoeks_dir = os.path.join(base_dir, 'RawInput')
constVerwijzingDir = os.path.join(base_dir, 'Verwijzingen')
constWelDir = os.path.join(onderzoeks_dir, "wel")
constNietDir = os.path.join(onderzoeks_dir, "niet")

controleText = '_gecontroleerd_'
imageList_P = [f for f in gevonden_files_onder_dir(constWelDir, '.jpg') if controleText not in f]
imageList_P.sort()
imageList_geen_P = [f for f in gevonden_files_onder_dir(constNietDir, '.jpg') if controleText not in f]
imageList_geen_P.sort()
dummyX = Viewer(imgList=imageList_geen_P, titel="NIET", aanleidingTotVeranderen="wel")
dummyX = None
dummyY = Viewer(imgList=imageList_P, titel="WEL", aanleidingTotVeranderen="niet")
dummyY = None


# Testen of er nog files niet gecontroleerd zijn
lijst_niet_gecontroleerd = [f for f in gevonden_files_onder_dir(constWelDir, '.jpg') if controleText not in f]
lijst_niet_gecontroleerd.extend([f for f in gevonden_files_onder_dir(constNietDir, '.jpg') if controleText not in f])

if len(lijst_niet_gecontroleerd) > 0:
    print('Er moeten nog ' + str(len(lijst_niet_gecontroleerd)) + ' gecontroleerd.')
else:
    voorbereidingVerwijzingenLijst = [os.path.join(constVerwijzingDir, f) for f in os.listdir(constVerwijzingDir)
                                      if os.path.isfile(os.path.join(constVerwijzingDir, f))]
    welHashes = [f[: hash_size * 4] for f in os.listdir(constWelDir)]
    for voorbereiding_verwijzingen_file in voorbereidingVerwijzingenLijst:
        hashes_en_verwijzingen = readDictFile(voorbereiding_verwijzingen_file)
        verwijzing_lijst = []
        for image_hash, verwijzing in hashes_en_verwijzingen.items():
            # Zoek of hij in wel of niet zit
            if image_hash in welHashes:
                verwijzing_lijst.append(verwijzing)
        if len(verwijzing_lijst) > 0:
            # Filenaam omzetten naar dirnaam door .txt er af te laten vallen
            dir_naam = voorbereiding_verwijzingen_file[:-4]
            write_na_te_lopen_verwijzingen_directorie(dir_naam, verwijzing_lijst)
        silentremove(voorbereiding_verwijzingen_file)
    print("lijsten klaargezet")
