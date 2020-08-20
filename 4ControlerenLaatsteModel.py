import os

import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as metrics
from keras import models
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras import applications
from generiekeFuncties.plaatjesFuncties import getTargetPictureSize
from datetime import datetime

# Wat willen we bekijken?
# train: 0
# test: 1
# validatie: 2
# oorspronkelijke bron: 3
directoryNr = 2
aantal = 25

#[[ 42397   1483]
# [  1955 180209]]

imageSize = getTargetPictureSize()

classifier = models.load_model(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                            'BesteModellen/besteModelResnetV2'))

base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
oorspronkelijke_bron_dir = '/mnt/GroteSchijf/machineLearningPictures/take1/volledigeSetVierBijVier'
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

datagen = ImageDataGenerator(preprocessing_function=applications.inception_resnet_v2.preprocess_input)
generator = datagen.flow_from_directory(
    onderzoeks_dir,
    target_size=(imageSize, imageSize),
    batch_size=20,
    class_mode='binary',
    shuffle=False)
steps_per_epoch = np.math.ceil(generator.samples / generator.batch_size)

predictions = classifier.predict(generator, steps=steps_per_epoch)
# Get most likely class

predicted_classes = np.around(predictions).flatten().astype(int)

print("############### klaar met voorspellen: ", str(datetime.now()))

true_classes = generator.classes
class_labels = list(generator.class_indices.keys())

report = metrics.classification_report(true_classes, predicted_classes, target_names=class_labels)
print(report)

confusion_matrix = metrics.confusion_matrix(y_true=true_classes, y_pred=predicted_classes)  # shape=(12, 12)

labels = ['wel', 'niet']

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

imageList_onterecht_P      = [(os.path.join(onderzoeks_dir, generator.filenames[i]), predictions[i]) for i in range(0, len(true_classes)) if true_classes[i] < predicted_classes[i]]
imageList_onterecht_P.sort(key = lambda x: -x[1])
imageList_onterecht_geen_P = [(os.path.join(onderzoeks_dir, generator.filenames[i]), predictions[i]) for i in range(0, len(true_classes)) if true_classes[i] > predicted_classes[i]]
imageList_onterecht_geen_P.sort(key = lambda x: x[1])

#imageName = predictions.
for img_path, img_value in imageList_onterecht_P[:min(aantal, len(imageList_onterecht_P))]:
    print("onterecht P: ", img_value)
    img = image.load_img(img_path, target_size=(imageSize, imageSize))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.
    plt.imshow(img_tensor[0])
    plt.show()

for img_path, img_value in imageList_onterecht_geen_P[:min(aantal, len(imageList_onterecht_geen_P))]:
    print("onterecht geen P: ", img_value)
    img = image.load_img(img_path, target_size=(imageSize, imageSize))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.
    plt.imshow(img_tensor[0])
    plt.show()


#layer_outputs = [layer.output for layer in classifier.layers[:12]] # Extracts the outputs of the top 12 layers
#activation_model = models.Model(inputs=classifier.input, outputs=layer_outputs) # Creates a model that will return these outputs, given the model input

#i=1