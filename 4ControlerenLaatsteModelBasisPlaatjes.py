import os

import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as metrics
from tensorflow.keras import models, preprocessing
from keras.preprocessing.image import ImageDataGenerator
from keras import applications
from datetime import datetime
from generiekeFuncties.plaatjesFuncties import get_target_picture_size, convert_image_to_square
from generiekeFuncties.utilities import verwijderGecontroleerdeFiles
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.fileHandlingFunctions import give_list_of_images
from PIL import Image

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

def geformatteerd_image_goedgekeurd(classifier, image):
    pp_image = preprocessing.image.img_to_array(image)
    try:
        np_image= np.array(pp_image)
    except ValueError as e:
        return -1
    #print("shape ", str(np_imgs.shape))
    np_image = np.expand_dims(np.array(np_image).astype(float), axis=0)
    np_image /= 255.0
    #np_imgs = applications.inception_resnet_v2.preprocess_input(np_imgs) lijkt niet te werken
    classifications = classifier.predict(np_image)
    max_classification = np.amax(classifications)
    return max_classification


onderzoeks_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/ontdubbeldEnVerkleind'
print("############### start: ", str(datetime.now()))

files = give_list_of_images(onderzoeks_dir, "niet")

for file in files:
    img = Image.open(os.path.join(onderzoeks_dir, "niet", file))
    b, h, img = convert_image_to_square(img, imageSize)
    geformatteerd_image_goedgekeurd(classifier=classifier, image=img)

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

imageList_onterecht_P = verwijderGecontroleerdeFiles(imageList_onterecht_P)
imageList_onterecht_geen_P = verwijderGecontroleerdeFiles(imageList_onterecht_geen_P)

viewer = Viewer(imgList=imageList_onterecht_P, titel="GEREGISTREERD ALS NIET ", aanleidingTotVeranderen="wel")

Viewer(imgList=imageList_onterecht_geen_P, titel="GEREGISTREERD ALS WEL", aanleidingTotVeranderen="niet")
