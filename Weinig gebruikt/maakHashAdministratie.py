from generiekeFuncties.fileHandlingFunctions import write_na_te_lopen_verwijzingen, readDictFile, writeDict
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image, download_image_naar_memory, sla_image_op, hashPicture, bigHashPicture

urlDict = readDictFile('/mnt/GroteSchijf/machineLearningPictures/verwijzingenBoekhouding/benaderde_urls.txt')

hashDict = {}

import os
import math
import shutil
from send2trash import send2trash
from PIL import Image
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, hashPicture, hash_size
from generiekeFuncties.fileHandlingFunctions import give_list_of_images
from generiekeFuncties.utilities import initializeerVoortgangsInformatie, geeftVoortgangsInformatie

import glob
from datetime import datetime

bestaande_files = [filename for filename in glob.iglob('/mnt/GroteSchijf/machineLearningPictures/take1/rawInput/**/*.jpg', recursive=True)]
for file in bestaande_files:
    img = Image.open(file)
    hash = bigHashPicture(img)
    hashDict[hash] = str(datetime.now())

# for url, datum in urlDict.items():
#     img = download_image_naar_memory(url_in=url)
#     if img is not None:
#         hash = bigHashPicture(img)
#         hashDict[hash] = datum

writeDict(hashDict, '/mnt/GroteSchijf/machineLearningPictures/verwijzingenBoekhouding/benaderde_hash.txt')

i=1