from datetime import datetime
from collections import defaultdict
import os
from generiekeFuncties.fileHandlingFunctions import lees_file_regels_naar_ontdubbelde_lijst

now = datetime.now()

constVerwijzingDir = '/mnt/GroteSchijf/machineLearningPictures/verwijzingen/boekhouding'
constBenaderde_url_administratie_pad = os.path.join(constVerwijzingDir, 'benaderde_urls.txt')

benaderde_url_administratie = lees_file_regels_naar_ontdubbelde_lijst(constBenaderde_url_administratie_pad)

def writeDictSavely(dict, fileName):
    savePath = fileName + str(datetime.now()) +".txt"
    if os.path.exists(fileName):
        os.rename(fileName, savePath)
    with open(fileName, 'w') as f:
       [f.write('{0},{1}\n'.format(key, value)) for key, value in dict.items()]


def readDictFile(path):
    d = defaultdict(str)
    with open(path,'r') as r:
        for line in r:
            splitted = line.strip().split(',')
            name = splitted[0].strip()
            value = splitted[1].strip()
            d[name]=value
    return d



dict = readDictFile(constBenaderde_url_administratie_pad)
writeDictSavely(dict, constBenaderde_url_administratie_pad)
i=1
