from generiekeFuncties.fileHandlingFunctions import write_voorbereiding_na_te_lopen_verwijzingen, readDictFile, writeDict
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image, download_image_naar_memory, sla_image_op, hashPicture, bigHashPicture

hashDict = readDictFile('/mnt/GroteSchijf/machineLearningPictures/verwijzingenBoekhouding/benaderde_hash2.txt')

from PIL import Image

import glob
from datetime import datetime

bestaande_files = [filename for filename in glob.iglob('/mnt/GroteSchijf/machineLearningPictures/take1/ontdubbeldEnVerkleind/**/*.jpg', recursive=True)]
for file in bestaande_files:
    img = Image.open(file)
    hash = bigHashPicture(img)
    if hash not in hashDict:
        hashDict[hash] = str(datetime.now())

writeDict(hashDict, '/mnt/GroteSchijf/machineLearningPictures/verwijzingenBoekhouding/benaderde_hash2.txt')