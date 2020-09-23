from PIL import Image, ImageStat
import imagehash
import os
from generiekeFuncties.fileHandlingFunctions import give_list_of_images
import shutil

# The path to the directory where the original
# data set was uncompressed
root = '/mnt/GroteSchijf/machineLearningPictures/take1'
full_data_set_dir = os.path.join(root, 'XrawVerwerkt')


fileNames = [os.path.join(full_data_set_dir, 'wel', f) for f in give_list_of_images(subdirName='wel', baseDir=full_data_set_dir)]
fileNames.extend([os.path.join(full_data_set_dir, 'niet', f) for f in give_list_of_images(subdirName='niet', baseDir=full_data_set_dir)])

phash8 = {}
phash16 = {}

for filename in fileNames:
    im = Image.open(filename)
    # imagehash.phash(im, hash_size=5)  12769 maar veel oneigenlijk
    # imagehash.phash(im, hash_size=6)  6164 maar veel oneigenlijk
    # magehash.phash(im, hash_size= 7)  1896 geen oneigenlijk gezien
    # magehash.phash(im, hash_size= 8)  1723 geen oneigenlijk gezien
    hash = imagehash.phash(im, hash_size=8)
    if hash in phash16:
        phash16[hash].append(filename)
    else:
        phash16[hash] = [filename]

dubbelen = {key: value for key, value in phash16.items() if len(value) > 1}

for k, v in dubbelen.items():
    i = 0
    for fn in v:
        shutil.copy(fn, os.path.join(full_data_set_dir, str(k) + str(i) + ".jpg"))
        i = i+1

i = 1