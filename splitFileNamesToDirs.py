import os, errno
import shutil

# root/level1/naam###blaadjes --> root/level1/naam/blaadjes
# recursief alle filenamen ophalen

fileNames = []
rt = '/mnt/GroteSchijf/VM/VM uitwisseling Experimenten/'

for root, directories, filenames in os.walk(rt):
     for filename in filenames:
             fileNames.append((root,filename))

mutateFrom = [os.path.join(pad, filenaam) for pad, filenaam in fileNames if len(str.split(filenaam, "###", 2)) == 2]
filenaamSplit = [(pad, str.split(filenaam, "###", 2)) for pad, filenaam in fileNames]
mutateTo = [os.path.join(rt, "nieuw", pad.replace(rt ,"") ,f[0], f[1]) for pad, f in filenaamSplit if len(f) == 2]
over = [(root, f) for pad, f in filenaamSplit if len(f) != 2]

if len(mutateFrom) == len(mutateTo):
    movedict = dict(zip(mutateFrom, mutateTo))
    for fileFrom, fileTo in movedict.items():
        if not os.path.exists(os.path.dirname(fileTo)):
            try:
                os.makedirs(os.path.dirname(fileTo))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        shutil.move(fileFrom, fileTo)
i = 1