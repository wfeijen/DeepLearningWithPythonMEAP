import os
import random
import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as metrics
from keras import models
from keras.preprocessing.image import ImageDataGenerator
from keras import applications
from datetime import datetime
import pyttsx3
import sys


sys.path.insert(0, os.getcwd())
from generiekeFuncties.plaatjesFuncties import get_target_picture_size
from generiekeFuncties.fileHandlingFunctions import (
    verwijderUitgecontroleerdeFilesFromList,
)
from generiekeFuncties.viewer import Viewer
from generiekeFuncties.neural_netwerk_maatwerk import recall_m, precision_m, f2_m


# aantal goedgeclassificeerde die we willen controleren
const_te_controleren_goed_geclassificeerd = 1000

imageSize = get_target_picture_size()

base_dir = "/media/willem/KleindSSD/machineLearningPictures/take1"
model_dir = "inceptionResnetV2_299"
modelPath = os.path.join(base_dir, "BesteModellen/inceptionResnetV2_299/m_")
onderzoeks_dir = os.path.join(base_dir, "OntdubbeldEnVerkleind")


def change_voice(engine, language, gender="VoiceGenderFemale"):
    for voice in engine.getProperty("voices"):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty("voice", voice.id)
            return True

    # raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))


engine = pyttsx3.init()
engine.say("Heeere we GOO")
engine.runAndWait()
print("############### start: ", str(datetime.now()))


image_generator = ImageDataGenerator(
    preprocessing_function=applications.inception_resnet_v2.preprocess_input
)
image_flow_from_directory = image_generator.flow_from_directory(
    onderzoeks_dir,
    target_size=(imageSize, imageSize),
    batch_size=20,
    class_mode="binary",
    shuffle=False,
)
steps_per_epoch = np.math.ceil(
    image_flow_from_directory.samples / image_flow_from_directory.batch_size
)

classifier = models.load_model(
    modelPath,
    custom_objects={"recall_m": recall_m, "precision_m": precision_m, "f2_m": f2_m},
)

print("############### start met voorspellen: ", str(datetime.now()))
predictions = classifier.predict(image_flow_from_directory, steps=steps_per_epoch)

# Get most likely class
predicted_classes = np.around(predictions).flatten().astype(int)

print("############### klaar met voorspellen: ", str(datetime.now()))

engine.say("And we are READY")
engine.runAndWait()

true_classes = image_flow_from_directory.classes
class_labels = list(image_flow_from_directory.class_indices.keys())

report = metrics.classification_report(
    true_classes, predicted_classes, target_names=class_labels
)
print(report)

confusion_matrix = metrics.confusion_matrix(
    y_true=true_classes, y_pred=predicted_classes
)  # shape=(12, 12)

labels = ["niet", "wel"]

print(confusion_matrix)
fig = plt.figure()
ax = fig.add_subplot(111)
cax = ax.matshow(confusion_matrix)
plt.title("Confusion matrix of the classifier")
fig.colorbar(cax)
ax.set_xticklabels([""] + labels)
ax.set_yticklabels([""] + labels)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()

# Terecht P
imageDict = [
    (image_flow_from_directory.filepaths[i], predictions[i])
    for i in range(0, len(true_classes))
    if true_classes[i] == predicted_classes[i] and true_classes[i] == 1
]
imageDict.sort(key=lambda x: abs(0.5 - x[1]) + random.uniform(0.0, 2.0))
werkelijk_W_voorspeld_W = [key for key, waarde in imageDict]
werkelijk_W_voorspeld_W = verwijderUitgecontroleerdeFilesFromList(
    werkelijk_W_voorspeld_W
)
werkelijk_W_voorspeld_W = werkelijk_W_voorspeld_W[
    : min(const_te_controleren_goed_geclassificeerd, len(werkelijk_W_voorspeld_W))
]

# Onterecht P
imageDict = [
    (image_flow_from_directory.filepaths[i], predictions[i])
    for i in range(0, len(true_classes))
    if true_classes[i] < predicted_classes[i]
]
imageDict.sort(key=lambda x: -x[1])
werkelijk_N_voorspeld_W = [key for key, waarde in imageDict]
werkelijk_N_voorspeld_W = verwijderUitgecontroleerdeFilesFromList(
    werkelijk_N_voorspeld_W
)

# Terecht geen P
imageDict = [
    (image_flow_from_directory.filepaths[i], predictions[i])
    for i in range(0, len(true_classes))
    if true_classes[i] == predicted_classes[i] and true_classes[i] == 0
]
imageDict.sort(key=lambda x: abs(0.5 - x[1]) + random.uniform(0.0, 2.0))
werkelijk_N_voorspeld_N = [key for key, waarde in imageDict]
werkelijk_N_voorspeld_N = verwijderUitgecontroleerdeFilesFromList(
    werkelijk_N_voorspeld_N
)
werkelijk_N_voorspeld_N = werkelijk_N_voorspeld_N[
    : min(const_te_controleren_goed_geclassificeerd, len(werkelijk_N_voorspeld_N))
]

# Onterecht geen P
imageDict = [
    (image_flow_from_directory.filepaths[i], predictions[i])
    for i in range(0, len(true_classes))
    if true_classes[i] > predicted_classes[i]
]
imageDict.sort(key=lambda x: x[1])
werkelijk_W_voorspeld_N = [key for key, waarde in imageDict]
werkelijk_W_voorspeld_N = verwijderUitgecontroleerdeFilesFromList(
    werkelijk_W_voorspeld_N
)


dummy = viewer = Viewer(
    imgList=werkelijk_W_voorspeld_W,
    titel="Goed geclassificeerd ",
    aanleidingTotVeranderen="niet",
)
dummy = None
dummy = viewer = Viewer(
    imgList=werkelijk_N_voorspeld_W,
    titel="GEREGISTREERD ALS NIET ",
    aanleidingTotVeranderen="wel",
)
dummy = None
dummy = Viewer(
    imgList=werkelijk_N_voorspeld_N,
    titel="Goed geclassificeerd ",
    aanleidingTotVeranderen="wel",
)
dummy = None
dummy = Viewer(
    imgList=werkelijk_W_voorspeld_N,
    titel="GEREGISTREERD ALS WEL",
    aanleidingTotVeranderen="niet",
)
