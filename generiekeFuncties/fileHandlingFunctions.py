import os, errno
import shutil
import random
from generiekeFuncties.plaatjesFuncties import get_square_images_from_file
import re
from collections import defaultdict
from datetime import datetime


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred


def give_list_of_images(subdirName, baseDir):
    data_set_dir = os.path.join(baseDir, subdirName)
    file_names = [f for f in os.listdir(data_set_dir) if os.path.isfile(os.path.join(data_set_dir, f))]
    return file_names

def make_subdirectory(subSubDirName, targetDir):
    target_sub_dir = os.path.join(targetDir, subSubDirName)
    os.mkdir(target_sub_dir)

def maak_directory_helemaal_leeg(dir):
    shutil.rmtree(dir)
    os.mkdir(dir)

def fill_subdirectory_with_squared_images(subSubDirName, targetDir, sourceDir, fileNames, targetSizeImage, minimaalVerschilInVerhoudingImages,rawVerwerktDir):
    source_data_set_dir = os.path.join(sourceDir, subSubDirName)
    target_data_set_dir = os.path.join(targetDir, subSubDirName)
    target_raw_verwerkt_dir = os.path.join(rawVerwerktDir, subSubDirName)
    subDirNr = 1000
    for file_name in fileNames:
        kale_file_naam, file_extension = os.path.splitext(file_name)
        file_naam_verwerkt_dir = os.path.join(target_raw_verwerkt_dir, file_name)
        file_naam_bron_dir = os.path.join(source_data_set_dir, file_name)
        im_list = get_square_images_from_file(imagePath=file_naam_bron_dir, targetSizeIm=targetSizeImage,
                                              minimaalVerschilInVerhoudingImages=minimaalVerschilInVerhoudingImages)
        i = 0
        for im in im_list:
            i = i+1
            dst = os.path.join(target_data_set_dir, int(subDirNr / 1000), kale_file_naam + str(i) + file_extension)
            subDirNr = subDirNr + 1
            im = im.convert('RGB')
            im.save(dst)
        shutil.move(file_naam_bron_dir, file_naam_verwerkt_dir)
    print(target_data_set_dir, ' total images:', len(os.listdir(target_data_set_dir)))


def make_and_fill_subdirectory_randomly_with_squared_images(subSubDirName, targetDir, sourceDir, rawVerwerktDir, fileNames, targetSizeImage):
    make_subdirectory(subSubDirName, targetDir)
    return fill_subdirectory_with_squared_images(subSubDirName, targetDir, sourceDir, fileNames, targetSizeImage, rawVerwerktDir)


def maak_doeldirectory_en_verplaats_random_files(subSubDirName, sourceDir, targetDir, numberOfFiles, fileNames):
    source_data_set_dir = os.path.join(sourceDir, subSubDirName)
    target_data_set_dir = os.path.join(targetDir, subSubDirName)
    os.mkdir(target_data_set_dir)
    for j in range(0, numberOfFiles):
        file_name = random.choice(fileNames)
        source_path = os.path.join(source_data_set_dir, file_name)
        destination_path =  os.path.join(target_data_set_dir, file_name)
        shutil.copyfile(source_path, destination_path)
        fileNames.remove(file_name)
    print(target_data_set_dir, ' total images:', len(os.listdir(target_data_set_dir)))
    return fileNames

def write_file_regels_naar_lijst(file_path, lijst):
    if os.path.exists(file_path):
        append_write = 'a'
    else:
        append_write = 'w'
    with open(file_path, append_write) as f:
        for item in lijst:
            f.write("%s\n" % item)
    f.close()

def lees_file_regels_naar_ontdubbelde_lijst(fileName):
    write_file_regels_naar_lijst(fileName, []) # We schrijven een lege regel zodat de file gemaakt wordt als hij nog niet bestaat
    with open(fileName, 'r') as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    f.close()
    return list(set(content))


def write_na_te_lopen_verwijzingen(root, url, postName, verwijzingen):
    # first we create a filename
    dir_name = os.path.join(root,  re.sub('[\W_]', '_', str(url.split('/')[4]) + '_' + postName))
    try:
        os.mkdir(dir_name)
    except:
        print("Directory ", dir_name, ' niet gemaakt. Bestond waarschijnlijk al.')
    file_path = os.path.join(dir_name, 'verwijzingen.txt')
    write_file_regels_naar_lijst(file_path, verwijzingen)


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