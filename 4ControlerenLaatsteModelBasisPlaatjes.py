import os

import matplotlib.pyplot as plt
import sklearn.metrics as metrics
from tensorflow.keras import models
from datetime import datetime
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, classificeer_vollig_image
from generiekeFuncties.utilities import verwijderGecontroleerdeFilesFromList, combine_lists, initializeerVoortgangsInformatie, geeftVoortgangsInformatie
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.fileHandlingFunctions import give_list_of_images
from PIL import Image

imageSize = get_target_picture_size()
start_tijd, vorige_tijd = initializeerVoortgangsInformatie("start")
classifier = models.load_model(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                            'BesteModellen/besteModelResnetV2'))

#onderzoeks_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/ontdubbeldEnVerkleind'
onderzoeks_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/testset'
print("############### start: ", str(datetime.now()))

def classificeer_volledige_image_lijst(image_lijst, classifier, imageSize):
    goede_image_lijst = []
    classificatie_lijst = []
    afgeronde_classificatie_lijst = []
    for file in image_lijst:
        classification = classificeer_vollig_image(file, classifier, imageSize)
        if classification >= 0:
            goede_image_lijst.append(file)
            classificatie_lijst.append(classification)
            if classification > 0.5:
                afgeronde_classificatie_lijst.append(1)
            else:
                afgeronde_classificatie_lijst.append(0)
    return goede_image_lijst, classificatie_lijst, afgeronde_classificatie_lijst


nietFiles = [os.path.join(onderzoeks_dir, "niet", file) for file in give_list_of_images(onderzoeks_dir, "niet")]
nietFiles, nietClassificaties, nietClassificatiesAfgerond = classificeer_volledige_image_lijst(nietFiles, classifier, imageSize)
welFiles = [os.path.join(onderzoeks_dir, "wel", file) for file in give_list_of_images(onderzoeks_dir, "wel")]
welFiles, welClassificaties, welClassificatiesAfgerond = classificeer_volledige_image_lijst(welFiles, classifier, imageSize)

alleFiles = combine_lists(nietFiles, welFiles)
alleClassificaties = combine_lists(nietClassificaties, welClassificaties)
alleClassificatiesAfgerond = combine_lists(nietClassificatiesAfgerond, welClassificatiesAfgerond)
alleWerkelijkeClasses = combine_lists([0] * len(nietFiles), [1] * len(welFiles))
alleClassLabels = combine_lists(['niet'] * len(nietFiles), ['wel'] * len(welFiles))
labels = ['niet', 'wel']

vorige_tijd = geeftVoortgangsInformatie("Klaar met voorspellen ", (start_tijd, vorige_tijd))

report = metrics.classification_report(alleWerkelijkeClasses, alleClassificatiesAfgerond, target_names=labels)
print(report)

confusion_matrix = metrics.confusion_matrix(y_true=alleWerkelijkeClasses, y_pred=alleClassificatiesAfgerond )  # shape=(12, 12)



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


imageDict_onterecht_P = [(nietFiles[i], nietClassificaties[i]) for i in
                         range(0, len(nietClassificaties)) if nietClassificatiesAfgerond[i] == 1]
imageDict_onterecht_P.sort(key=lambda x: -x[1])
imageList_onterecht_P = [key for key, waarde in imageDict_onterecht_P]
imageDict_onterecht_geen_P = [(welFiles[i], welClassificaties[i]) for i in
                              range(0, len(welClassificaties)) if welClassificatiesAfgerond[i] == 0]
imageDict_onterecht_geen_P.sort(key=lambda x: x[1])
imageList_onterecht_geen_P = [key for key, waarde in imageDict_onterecht_geen_P]

imageList_onterecht_P = verwijderGecontroleerdeFilesFromList(imageList_onterecht_P)
imageList_onterecht_geen_P = verwijderGecontroleerdeFilesFromList(imageList_onterecht_geen_P)

viewer = Viewer(imgList=imageList_onterecht_P, titel="GEREGISTREERD ALS NIET ", aanleidingTotVeranderen="wel")

Viewer(imgList=imageList_onterecht_geen_P, titel="GEREGISTREERD ALS WEL", aanleidingTotVeranderen="niet")
