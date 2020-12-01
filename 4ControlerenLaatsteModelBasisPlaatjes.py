import os
import random

import matplotlib.pyplot as plt
import sklearn.metrics as metrics
from tensorflow.keras import models
from datetime import datetime
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image_from_file
from generiekeFuncties.utilities import combine_lists, \
    initializeerVoortgangsInformatie, geeftVoortgangsInformatie
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.fileHandlingFunctions import give_list_of_images, verwijderGecontroleerdeFilesBovenNummerFromList
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m

base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
modelPath = os.path.join(base_dir, 'BesteModellen/m_')
onderzoeks_dir = os.path.join(base_dir, 'OntdubbeldEnVerkleind')

# onderzoeks_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/testset'

start_tijd, vorige_tijd = initializeerVoortgangsInformatie("start")
classifier = models.load_model(modelPath,
                               custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})
imageSize = get_target_picture_size()
print("############### start: ", str(datetime.now()))


def classificeer_volledige_image_lijst(image_lijst, klassificator, image_size):
    tijden = initializeerVoortgangsInformatie("start classificeren volledige lijst")
    goede_image_lijst = []
    classificatie_lijst = []
    afgeronde_classificatie_lijst = []
    procent = int(len(image_lijst) / 100)
    i = 0
    j = 0
    for file in image_lijst:
        i = i + 1
        if i >= procent:
            j = j + 1
            i = 0
            tijden = geeftVoortgangsInformatie("We zijn op:" + str(j) + "% ", tijden)
        classification = classificeer_vollig_image_from_file(file, klassificator, image_size)
        if classification >= 0:
            goede_image_lijst.append(file)
            classificatie_lijst.append(classification)
            if classification > 0.5:
                afgeronde_classificatie_lijst.append(1)
            else:
                afgeronde_classificatie_lijst.append(0)
    return goede_image_lijst, classificatie_lijst, afgeronde_classificatie_lijst


nietFiles = [os.path.join(onderzoeks_dir, "niet", file) for file in give_list_of_images(onderzoeks_dir, "niet")]
nietFiles, nietClassificaties, nietClassificatiesAfgerond = classificeer_volledige_image_lijst(nietFiles,
                                                                                               classifier,
                                                                                               imageSize)
welFiles = [os.path.join(onderzoeks_dir, "wel", file) for file in give_list_of_images(onderzoeks_dir, "wel")]
welFiles, welClassificaties, welClassificatiesAfgerond = classificeer_volledige_image_lijst(welFiles,
                                                                                            classifier,
                                                                                            imageSize)

alleFiles = combine_lists(nietFiles, welFiles)
alleClassificaties = combine_lists(nietClassificaties, welClassificaties)
alleClassificatiesAfgerond = combine_lists(nietClassificatiesAfgerond, welClassificatiesAfgerond)
alleWerkelijkeClasses = combine_lists([0] * len(nietFiles), [1] * len(welFiles))
alleClassLabels = combine_lists(['niet'] * len(nietFiles), ['wel'] * len(welFiles))
labels = ['niet', 'wel']

vorige_tijd = geeftVoortgangsInformatie("Klaar met voorspellen ", (start_tijd, vorige_tijd))

report = metrics.classification_report(alleWerkelijkeClasses, alleClassificatiesAfgerond, target_names=labels)
print(report)

confusion_matrix = metrics.confusion_matrix(y_true=alleWerkelijkeClasses,
                                            y_pred=alleClassificatiesAfgerond)  # shape=(12, 12)

print(confusion_matrix)
fig = plt.figure()
ax = fig.add_subplot(111)
cax = ax.matshow(confusion_matrix)
plt.title('Confusion matrix of the classifier')
fig.colorbar(cax)
ax.set_xticklabels([''] + labels)
ax.set_yticklabels([''] + labels)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.show()


imageDict_terecht_geen_P = [(nietFiles[i], nietClassificaties[i]) for i in
                         range(0, len(nietClassificaties)) if nietClassificatiesAfgerond[i] == 0]
imageList_terecht_geen_P = [key for key, waarde in imageDict_terecht_geen_P]
imageDict_onterecht_P = [(nietFiles[i], nietClassificaties[i]) for i in
                         range(0, len(nietClassificaties)) if nietClassificatiesAfgerond[i] == 1]
imageList_onterecht_P = [key for key, waarde in imageDict_onterecht_P]
imageDict_terecht_P = [(welFiles[i], welClassificaties[i]) for i in
                              range(0, len(welClassificaties)) if welClassificatiesAfgerond[i] == 1]
imageList_terecht_P = [key for key, waarde in imageDict_terecht_P]
imageDict_onterecht_geen_P = [(welFiles[i], welClassificaties[i]) for i in
                              range(0, len(welClassificaties)) if welClassificatiesAfgerond[i] == 0]
imageList_onterecht_geen_P = [key for key, waarde in imageDict_onterecht_geen_P]

imageList_onterecht_geen_P = verwijderGecontroleerdeFilesBovenNummerFromList(imageList_onterecht_geen_P, 2)
imageList_onterecht_P = verwijderGecontroleerdeFilesBovenNummerFromList(imageList_onterecht_P, 2)
imageList_terecht_P = random.sample(verwijderGecontroleerdeFilesBovenNummerFromList(imageList_terecht_P, 2)
                                    , len(imageList_onterecht_P))
imageList_terecht_geen_P = random.sample(verwijderGecontroleerdeFilesBovenNummerFromList(imageList_terecht_geen_P, 2)
                                         , len(imageList_onterecht_geen_P))

# Viewer(imgList=imageList_terecht_P, titel="TERECHT geclassificeerd als WEL ", aanleidingTotVeranderen="niet")
Viewer(imgList=imageList_onterecht_P, titel="ONTERECHT geclassificeerd als WEL ", aanleidingTotVeranderen="wel")
# Viewer(imgList=imageList_terecht_geen_P, titel="TERECHT geclassificeerd als NIET", aanleidingTotVeranderen="wel")
Viewer(imgList=imageList_onterecht_geen_P, titel="ONTERECHT geclassificeerd als NIET", aanleidingTotVeranderen="niet")
