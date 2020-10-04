import os, errno
import shutil
import random
from generiekeFuncties.plaatjesFuncties import convertImageToSquareIm_from_file
import re
from collections import defaultdict
import requests
from io import BytesIO



def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def give_list_of_images(baseDir, subdirName):
    data_set_dir = os.path.join(baseDir, subdirName)
    file_names = [f for f in os.listdir(data_set_dir) if os.path.isfile(os.path.join(data_set_dir, f))]
    return file_names


def make_subdirectory(subSubDirName, targetDir):
    target_sub_dir = os.path.join(targetDir, subSubDirName)
    os.mkdir(target_sub_dir)


def maak_directory_helemaal_leeg(dir):
    shutil.rmtree(dir)
    os.mkdir(dir)


def fill_subdirectory_with_squared_images(subSubDirName, targetDir,
                                          sourceDir, fileNames, targetSizeImage,
                                          rawVerwerktDir, subdirSize=5000):
    source_data_set_dir = os.path.join(sourceDir, subSubDirName)
    target_data_set_dir = os.path.join(targetDir, subSubDirName)
    target_raw_verwerkt_dir = os.path.join(rawVerwerktDir, subSubDirName)
    sub_dir_nr = subdirSize
    for file_name in fileNames:
        file_naam_verwerkt_dir = os.path.join(target_raw_verwerkt_dir, file_name)
        file_naam_bron_dir = os.path.join(source_data_set_dir, file_name)
        sx, sy, im = convertImageToSquareIm_from_file(imagePath=file_naam_bron_dir, targetSizeIm=targetSizeImage)
        if im is None:
            print("image niet te verwerken. Afmetingen: ", str(sx), "x", str(sy))
        else:
            im = im.convert('RGB')
            dir = os.path.join(target_data_set_dir, str(int(sub_dir_nr / subdirSize)))
            if not os.path.exists(dir):
                os.mkdir(dir)
            dst = os.path.join(dir, file_name)
            im.save(dst)
            sub_dir_nr = sub_dir_nr + 1
        shutil.move(file_naam_bron_dir, file_naam_verwerkt_dir)
    print(target_data_set_dir, ' 1000 tal images:', len(os.listdir(target_data_set_dir)))


def make_and_fill_subdirectory_randomly_with_squared_images(subSubDirName, targetDir, sourceDir, rawVerwerktDir,
                                                            fileNames, targetSizeImage):
    make_subdirectory(subSubDirName, targetDir)
    return fill_subdirectory_with_squared_images(subSubDirName, targetDir, sourceDir, fileNames, targetSizeImage,
                                                 rawVerwerktDir)


def maak_doeldirectory_en_verplaats_random_files(subSubDirName, sourceDir, targetDir, numberOfFiles, fileNames):
    source_data_set_dir = os.path.join(sourceDir, subSubDirName)
    target_data_set_dir = os.path.join(targetDir, subSubDirName)
    os.mkdir(target_data_set_dir)
    for j in range(0, numberOfFiles):
        file_name = random.choice(fileNames)
        source_path = os.path.join(source_data_set_dir, file_name)
        destination_path = os.path.join(target_data_set_dir, file_name)
        shutil.copyfile(source_path, destination_path)
        fileNames.remove(file_name)
    print(target_data_set_dir, ' total images:', len(os.listdir(target_data_set_dir)))
    return fileNames

def maak_subdirectory_en_vul_met_random_squared_images(subSubDirName, targetDir,
                                          sourceDir, numberOfFiles, fileNames, targetSizeImage):
    source_data_set_dir = os.path.join(sourceDir, subSubDirName)
    target_data_set_dir = os.path.join(targetDir, subSubDirName)
    if not os.path.exists(target_data_set_dir):
        os.mkdir(target_data_set_dir)
    for j in range(0, numberOfFiles):
        file_name = random.choice(fileNames)
        fileNames.remove(file_name)
        file_naam_bron_dir = os.path.join(source_data_set_dir, file_name)
        sx, sy, im = convertImageToSquareIm_from_file(imagePath=file_naam_bron_dir, targetSizeIm=targetSizeImage)
        if im is None:
            print("image niet te verwerken. Afmetingen: ", str(sx), "x", str(sy))
        else:
            im = im.convert('RGB')
            dst = os.path.join(target_data_set_dir, file_name)
            im.save(dst)
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
    write_file_regels_naar_lijst(fileName,
                                 [])  # We schrijven een lege regel zodat de file gemaakt wordt als hij nog niet bestaat
    with open(fileName, 'r') as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    f.close()
    return list(set(content))


def write_voorbereiding_na_te_lopen_verwijzingen(root, url, postName, url_verwijzingen_en_lokale_file_hash):
    # first we create a filename
    file_path = os.path.join(root, re.sub('[\W_]', '_', str(url.split('/')[4]) + '_' + postName) + '.txt')
    regels = [key + "," + value for key, value in url_verwijzingen_en_lokale_file_hash.items()]
    write_file_regels_naar_lijst(file_path, regels)

def write_na_te_lopen_verwijzingen_directorie(dir_name, verwijzingen):
    try:
        os.mkdir(dir_name)
    except Exception as e:
        print("Directory ", dir_name, ' niet gemaakt. Bestond waarschijnlijk al.', str(e))
    file_path = os.path.join(dir_name, 'verwijzingen.txt')
    write_file_regels_naar_lijst(file_path, verwijzingen)


def writeDict(dict, fileName):
    with open(fileName, 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in dict.items()]


def readDictFile(path):
    d = defaultdict(str)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('')
    with open(path, 'r') as r:
        for line in r:
            splitted = line.strip().split(',')
            name = splitted[0].strip()
            value = splitted[1].strip()
            d[name] = value
    return d


def veranderVanKant(file_pad_in):
    pad_delen = os.path.split(file_pad_in)
    if pad_delen[0][-4:] == "niet":
        a = pad_delen[0][:-4] + "wel"
    else:
        a = pad_delen[0][:-3] + "niet"
    b = pad_delen[1][:-4] + "_gecontroleerd.jpg"
    nieuw_pad = os.path.join(a, b)
    os.rename(file_pad_in, nieuw_pad)
    return nieuw_pad


def markeerGecontroleerd(file_pad_in):
    pad_delen = os.path.split(file_pad_in)
    a = pad_delen[0]
    b = pad_delen[1][:-4] + "_gecontroleerd.jpg"
    nieuw_pad = os.path.join(a, b)
    os.rename(file_pad_in, nieuw_pad)
    return nieuw_pad

def prioriteerGecontroleerd(fileList, aantal):
    # Verdeel in twee delen
    gecontroleerdeFiles = []
    nietGecontroleerdeFiles = []
    for file in fileList:
        if file.endswith("gecontroleerd.jpg"):
            gecontroleerdeFiles.append(file)
        else:
            nietGecontroleerdeFiles.append(file)
    print("Aantal gecontroleerde files: ", str(len(gecontroleerdeFiles)), " van de ", aantal)
    gecontroleerdeFiles.extend(nietGecontroleerdeFiles[:aantal - len(gecontroleerdeFiles)])
    return gecontroleerdeFiles[:aantal]






