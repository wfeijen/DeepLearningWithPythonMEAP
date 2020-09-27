import os

import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as metrics
from keras import models
from keras.preprocessing.image import ImageDataGenerator
from keras import applications
from datetime import datetime
from generiekeFuncties.plaatjesFuncties import get_target_picture_size
from generiekeFuncties.utilities import verwijderGecontroleerdeFilesFromList
from generiekeFuncties.viewer import Viewer

# Wat willen we bekijken?
# train: 0
# test: 1
# validatie: 2
# oorspronkelijke bron: 3
directoryNr = 3

# Ongedaan maken gecontroleerd: find . -type f -exec rename -n 's/gecontroleerd//' {} +

# [[ 42397   1483]
# [  1955 180209]]

imageSize = get_target_picture_size()

classifier = models.load_model(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                            'BesteModellen/besteModelResnetV2'))

base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
oorspronkelijke_bron_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/volledigeSetVierBijVier240'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
if directoryNr == 0:
    onderzoeks_dir = train_dir
elif directoryNr == 1:
    onderzoeks_dir = test_dir
elif directoryNr == 2:
    onderzoeks_dir = validation_dir
else:
    onderzoeks_dir = oorspronkelijke_bron_dir

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

imageList_onterecht_P = verwijderGecontroleerdeFilesFromList(imageList_onterecht_P)
imageList_onterecht_geen_P = verwijderGecontroleerdeFilesFromList(imageList_onterecht_geen_P)

viewer = Viewer(imgList=imageList_onterecht_P, titel="GEREGISTREERD ALS NIET ", aanleidingTotVeranderen="wel")

Viewer(imgList=imageList_onterecht_geen_P, titel="GEREGISTREERD ALS WEL", aanleidingTotVeranderen="niet")
