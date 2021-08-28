from generiekeFuncties.fileHandlingFunctions import write_voorbereiding_na_te_lopen_verwijzingen, readDictFile, writeDict
import os


base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
constBenaderde_hash_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_hash.txt')
constBenaderde_hash_nieuw_administratie_pad = os.path.join(base_dir, 'VerwijzingenBoekhouding/benaderde_hash_n.txt')
hash_administratie = readDictFile(constBenaderde_hash_administratie_pad)

tuples = [(key, value, 10000, 10000, 10000) for key, value in hash_administratie.items()]

with open(constBenaderde_hash_nieuw_administratie_pad, 'w') as f:
    for tuple in tuples:
        f.write('%s,%s,%d,%d,%d\n' % tuple)


i = 1

# with open('file_name', 'w') as f:
#     for tuple in tuples:
#         f.write('%s %s %s\n' % tuple)
#
# def writeTuple(dict, fileName):
#     with open(fileName, 'w') as f:
#         [f.write('{0},{1}\n'.format(key, value)) for key, value in dict.items()]
#
#
# def readDictFile(path):
#     d = defaultdict(str)
#     if not os.path.exists(path):
#         with open(path, 'w') as f:
#             f.write('')
#     with open(path, 'r') as r:
#         for line in r:
#             splitted = line.strip().split(',', 1)
#             name = splitted[0].strip()
#             value = splitted[1].strip()
#             d[name] = value
#     return d