import os

import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as metrics
from keras import models
from keras.preprocessing.image import ImageDataGenerator
from keras import applications
from datetime import datetime
from generiekeFuncties.plaatjesFuncties import get_target_picture_size
from generiekeFuncties.fileHandlingFunctions import verwijderGecontroleerdeFilesBovenNummerFromList
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m

# Wat willen we bekijken?
# train: 0
# test: 1
# validatie: 2
directoryNr = 2


imageSize = get_target_picture_size()

base_dir = '/mnt/GroteSchijf/machineLearningPictures/take1'
model_dir = 'inceptionResnetV2_299'
modelPath = os.path.join(base_dir, 'BesteModellen', model_dir, 'm_')
onderzoeks_dir = os.path.join(base_dir, 'OntdubbeldEnVerkleind')

classifier = models.load_model(modelPath,
                               custom_objects={'recall_m': recall_m, 'precision_m': precision_m, "f2_m": f2_m})


print("############### start: ", str(datetime.now()))

image_generator = ImageDataGenerator(preprocessing_function=applications.inception_resnet_v2.preprocess_input)
image_flow_from_directory = image_generator.flow_from_directory(
    onderzoeks_dir,
    target_size=(imageSize, imageSize),
    batch_size=20,
    class_mode='binary',
    shuffle=False)
steps_per_epoch = np.math.ceil(image_flow_from_directory.samples / image_flow_from_directory.batch_size)

predictions = classifier.predict(image_flow_from_directory, steps=steps_per_epoch)
# Get most likely class

predicted_classes = np.around(predictions).flatten().astype(int)

print("############### klaar met voorspellen: ", str(datetime.now()))

true_classes = image_flow_from_directory.classes
class_labels = list(image_flow_from_directory.class_indices.keys())

report = metrics.classification_report(true_classes, predicted_classes, target_names=class_labels)
print(report)

confusion_matrix = metrics.confusion_matrix(y_true=true_classes, y_pred=predicted_classes)  # shape=(12, 12)

labels = ['niet', 'wel']

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

imageDict_onterecht_P = [(os.path.join(onderzoeks_dir, image_flow_from_directory.filenames[i]), predictions[i]) for i in
                         range(0, len(true_classes)) if true_classes[i] < predicted_classes[i]]
imageDict_onterecht_P.sort(key=lambda x: -x[1])
imageList_onterecht_P = [key for key, waarde in imageDict_onterecht_P]
imageDict_onterecht_geen_P = [(os.path.join(onderzoeks_dir, image_flow_from_directory.filenames[i]),
                               predictions[i]) for i in
                              range(0, len(true_classes)) if true_classes[i] > predicted_classes[i]]
imageDict_onterecht_geen_P.sort(key=lambda x: x[1])
imageList_onterecht_geen_P = [key for key, waarde in imageDict_onterecht_geen_P]

imageList_onterecht_P = verwijderGecontroleerdeFilesBovenNummerFromList(imageList_onterecht_P, 2)
imageList_onterecht_geen_P = verwijderGecontroleerdeFilesBovenNummerFromList(imageList_onterecht_geen_P, 2)

viewer = Viewer(imgList=imageList_onterecht_P, titel="GEREGISTREERD ALS NIET ", aanleidingTotVeranderen="wel")

Viewer(imgList=imageList_onterecht_geen_P, titel="GEREGISTREERD ALS WEL", aanleidingTotVeranderen="niet")
