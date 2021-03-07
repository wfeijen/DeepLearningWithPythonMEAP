import os, errno
import regex
import shutil
import random
import re
from collections import defaultdict, OrderedDict

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def move_file_en_maak_dir_als_nodig(bron_pad, doel_pad):
    os.makedirs(os.path.dirname(doel_pad), exist_ok=True)
    shutil.move(bron_pad, doel_pad)
    try:
        shutil.move(bron_pad + '.pp3', doel_pad + '.pp3')
    except FileNotFoundError as e:
        print(bron_pad + '.pp3 bestond niet')


def maak_directory_helemaal_leeg(dir):
    shutil.rmtree(dir)
    os.mkdir(dir)


def maak_doeldirectory_en_verplaats_random_files(subSubDirName, targetDir, numberOfFiles, fileNames):
    target_data_set_dir = os.path.join(targetDir, subSubDirName)
    os.mkdir(target_data_set_dir)
    for j in range(0, numberOfFiles):
        source_path = random.choice(fileNames)
        file_naam = os.path.basename(source_path)
        destination_path = os.path.join(target_data_set_dir, file_naam[0], file_naam[1], file_naam)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.copyfile(source_path, destination_path)
        fileNames.remove(source_path)
    print(target_data_set_dir)
    return fileNames


def write_lijst_regels_naar_file(file_path, lijst):
    if os.path.exists(file_path):
        append_write = 'a'
    else:
        append_write = 'w'
    with open(file_path, append_write) as f:
        for item in lijst:
            f.write("%s\n" % item)
    f.close()


def lees_file_regels_naar_ontdubbelde_lijst(fileName):
    write_lijst_regels_naar_file(fileName,
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
    write_lijst_regels_naar_file(file_path, regels)

def write_na_te_lopen_verwijzingen_directorie(dir_name, verwijzingen):
    try:
        os.mkdir(dir_name)
    except Exception as e:
        print("Directory ", dir_name, ' niet gemaakt. Bestond waarschijnlijk al.', str(e))
    file_path = os.path.join(dir_name, 'verwijzingen.txt')
    write_lijst_regels_naar_file(file_path, verwijzingen)


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

# 80772dca3644b9e7gecontroleerd.jpg
def get_hash_from_filename(file_naam_in):
    loc = file_naam_in.find("_gecontroleerd")
    if loc == -1:
        return file_naam_in[:-4] # alleen .jpg er af
    else:
        return file_naam_in[:loc]


def get_zekerheid_goede_classe(char, filenaam_in):
    # We zoeken naar een reeks van 0 naar 100
    # We pakken de reeks
    match = regex.findall('_gecontroleerd_([wn]+).jpg', filenaam_in, regex.IGNORECASE)
    if len(match) == 0:
        # Nog nooit gecontroleerd
        # Ongecontroleerd waarderen we op de helft
        return 50
    reeks = match[0]
    if len(reeks) == 0:
        return 51
    totaal_waarde = 0
    char_waarde = 0
    for i in range(0, len(reeks)):
        totaal_waarde += i + 1
        if reeks[i] == char:
            char_waarde += i + 1
    return (100 * (char_waarde + char_waarde - totaal_waarde) / totaal_waarde)


def get_controle_aantal_reeks(char, filenaam_in):
    if "_gecontroleer" not in filenaam_in:
        return 0
    f = filenaam_in[:-4]
    i = -1
    while f[i] == char:
        i = i - 1
    antwoord = -(1 + i)
    return antwoord


def markeerControleResultaat(file_naam_in, operatie):
    # Voegt de eerste letter van de operatie toe (n/w)
    filenaam_kort = file_naam_in[:-4]
    if "_gecontroleerd_" in file_naam_in:
        return filenaam_kort + operatie[0] + ".jpg"
    else:
        return get_hash_from_filename(file_naam_in) + "_gecontroleerd_" + operatie[0] + ".jpg"


# Gebruikt in viewer
def veranderVanKant(file_pad_in, operatie_in):
    pad = os.path.dirname(file_pad_in)
    if "/niet" in pad:
        a = pad.replace("/niet", "/wel")
    else:
        a = pad.replace("/wel", "/niet")
    b = markeerControleResultaat(os.path.basename(file_pad_in), operatie_in)
    nieuw_pad = os.path.join(a, b)
    move_file_en_maak_dir_als_nodig(file_pad_in, nieuw_pad)
    return nieuw_pad


def markeerGecontroleerd(file_pad_in, operatie_in):
    a = os.path.dirname(file_pad_in)
    b = markeerControleResultaat(os.path.basename(file_pad_in), operatie_in)
    nieuw_pad = os.path.join(a, b)
    move_file_en_maak_dir_als_nodig(file_pad_in, nieuw_pad)
    return nieuw_pad

# Gebruikt in verplaaatsNaarWerkset
def prioriteerGecontroleerd(fileList, aantal, controle_char):
    # Verdeel in twee delen
    antwoord = []
    fileGroepen = {}
    for file in fileList:
        waarschijnlijkheid_goede_classe = round(get_zekerheid_goede_classe(controle_char, file))
        if waarschijnlijkheid_goede_classe not in fileGroepen:
            fileGroepen[waarschijnlijkheid_goede_classe] = []
        fileGroepen[waarschijnlijkheid_goede_classe].append(file)
    fileGroepen = OrderedDict(reversed(sorted(fileGroepen.items())))

    i = 0
    for nr, fileGroep in fileGroepen.items():
        j = 0
        while i < aantal and len(fileGroep) > 0:
            i = i + 1
            j = j + 1
            file_name = fileGroep[random.randint(0, len(fileGroep) - 1)]
            fileGroep.remove(file_name)
            antwoord.append(file_name)
        print(str(j), " files rang ", nr , " toegevoegd ")
    print("totaal ", i, " files toegevoegd")
    return antwoord


def verwijderUitgecontroleerdeFilesFromList(fileList):
    antwoord = []
    for file in fileList:
        f = os.path.basename(file)
        if f.count('w') < 4\
                and f.count('n') < 4:
            antwoord.append(file)
    return antwoord


def gevonden_hashcodes_onder_dir(dir, hash_size):
    return([f[:hash_size * 2] for dp, dn, filenames in os.walk(dir) for f in filenames])


def gevonden_files_onder_dir(directory, ext):
    antwoord = ([os.path.join(root, f) for root, directorynamese, filenames in os.walk(directory) for f in filenames if f.endswith(ext)])
    return antwoord




# def give_list_of_images(baseDir, subdirName):
#     data_set_dir = os.path.join(baseDir, subdirName)
#     file_names = [f for f in os.listdir(data_set_dir) if os.path.isfile(os.path.join(data_set_dir, f))]
#     return file_names



