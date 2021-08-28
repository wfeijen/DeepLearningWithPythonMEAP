from PIL import Image, ImageStat
from send2trash import send2trash
from keras import preprocessing
import numpy as np
import requests
from io import BytesIO
import imagehash
import os
import re
from generiekeFuncties.fileHandlingFunctions import gevonden_files_onder_dir
import matplotlib
import matplotlib.pyplot as plt
import shutil
from generiekeFuncties.fileHandlingFunctions import write_voorbereiding_na_te_lopen_verwijzingen, readDictFile, writeDict
from fake_useragent import UserAgent
ua = UserAgent(verify_ssl=False)

import gmpy2

from generiekeFuncties.plaatjesFuncties import bigHashPicture

base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
modelPath = os.path.join(base_dir, 'BesteModellen/inceptionResnetV2_299/m_')
constVoorberVerwijzingDir = os.path.join(base_dir, 'Verwijzingen')
constBenaderde_hash_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_hash.txt')
hash_administratie1 = readDictFile(constBenaderde_hash_administratie_pad)
hash_administratie2 = hash_administratie1.copy()

results = []
gevondenHashes = {}
pad = '/home/willem/PycharmProjects/DeepLearningWithPythonMEAP/voorbeelden/gelijkeFiles'
filenames = gevonden_files_onder_dir(pad, '.jpg')
for fileName in filenames:
    fileNameKort = os.path.basename(fileName)
    im = Image.open(fileName)
    hashNieuw = str(imagehash.phash(im, hash_size=16))
    for eerdereHash, eerdereImage in gevondenHashes.items():
        afstand = gmpy2.popcount(int(hashNieuw, 16) ^ int(eerdereHash, 16))
        results.append((afstand, fileNameKort, eerdereImage))
    gevondenHashes[hashNieuw] = fileNameKort

resultsGesorteerd = sorted(results, key=lambda tup: (tup[0], tup[1], tup[2]))

for result in resultsGesorteerd:
    print(result)



