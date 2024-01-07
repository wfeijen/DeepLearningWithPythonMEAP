import os
import gc
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import applications
from tensorflow.keras.callbacks import ModelCheckpoint
import sys


sys.path.insert(0, os.getcwd())
from generiekeFuncties.presentationFunctions import plotLossAndAcc
from generiekeFuncties.plaatjesFuncties import get_target_picture_size
from generiekeFuncties.utilities import (
    geeft_voortgangs_informatie,
    initializeer_voortgangs_informatie,
)
from generiekeFuncties.neural_netwerk_maatwerk import (
    recall_m,
    precision_m,
    f2_m,
    zet_random_lagen_open_van_conv_base,
)

base_dir = "/media/willem/KleindSSD/machineLearningPictures/take1"
modelPath = os.path.join(base_dir, "BesteModellen/inceptionResnetV2_299/m_")
base_picture_dir = os.path.join(base_dir, "Werkplaats")
train_dir = os.path.join(base_picture_dir, "train")
validation_dir = os.path.join(base_picture_dir, "validation")
imageSize = get_target_picture_size()
batchSize = 16
sequences = range(3)
epochs_list = [20, 20, 20]
images_per_epoch_list = [20000, 20000, 20000]
aantal_lerende_lagen_conv_base_list = [30, 30, 30]

validation_images = 3000
start_Learning_rate_factor_list = [1, 0.7, 0.5]
initial_start_learning_rate = 0.0050

bestaandmodel_verder_brengen = True

start_Learning_rate_list = [
    initial_start_learning_rate * i for i in start_Learning_rate_factor_list
]
validation_steps = validation_images // batchSize + 1
tijdenVorigePunt = initializeer_voortgangs_informatie("start")

train_datagen = ImageDataGenerator(
    preprocessing_function=applications.inception_resnet_v2.preprocess_input,
    horizontal_flip=True,
)

# Note that the validation data should not be augmented!
# Maar een horizontale flip levert een plaatje op dat niet fout kan zijn dus dat doen we wel.
test_datagen = ImageDataGenerator(
    preprocessing_function=applications.inception_resnet_v2.preprocess_input,
    horizontal_flip=True,
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(imageSize, imageSize),
    batch_size=batchSize,
    shuffle=True,
    class_mode="binary",
)

validation_generator = test_datagen.flow_from_directory(
    validation_dir,
    target_size=(imageSize, imageSize),
    batch_size=batchSize,
    shuffle=True,
    class_mode="binary",
)


if bestaandmodel_verder_brengen:
    model = models.load_model(
        modelPath,
        custom_objects={"recall_m": recall_m, "precision_m": precision_m, "f2_m": f2_m},
    )
    print(
        "bestaand model geladen. Trainable weights = ",
        str(len(model.trainable_weights)),
    )
else:
    conv_base = applications.InceptionResNetV2(
        include_top=False, weights="imagenet", input_shape=(imageSize, imageSize, 3)
    )
    model = models.Sequential()
    model.add(conv_base)
    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation="relu"))
    model.add(layers.Dense(1, activation="sigmoid"))
    print(
        "This is the number of trainable weights before freezing the conv base:",
        len(model.trainable_weights),
    )
    conv_base.trainable = False
    # for layer in conv_base.layers[:-2]:
    #    layer.trainable = False
    print(
        "This is the number of trainable weights after freezing the conv base:",
        len(model.trainable_weights),
    )

print(model.summary())
print(model.layers)

checkpoint = ModelCheckpoint(
    modelPath,
    monitor="val_f2_m",
    verbose=1,
    save_best_only=True,
    save_weights_only=True,
    mode="max",
    period=1,
)
historyList = []

for i in sequences:
    steps_per_epoch = images_per_epoch_list[i] // batchSize + 1
    epochs = epochs_list[i]
    learning_rate = start_Learning_rate_list[i]
    aantal_lerende_lagen_conv_base = aantal_lerende_lagen_conv_base_list[i]
    tijdenVorigePunt = geeft_voortgangs_informatie(
        "##########################################################################",
        tijdenVorigePunt,
    )
    model = zet_random_lagen_open_van_conv_base(model, aantal_lerende_lagen_conv_base)
    tijdenVorigePunt = geeft_voortgangs_informatie(
        str(aantal_lerende_lagen_conv_base) + "lagen opgengezet. ", tijdenVorigePunt
    )
    print(
        "sequence: ",
        str(i),
        " epochs: ",
        epochs,
        " start lr: ",
        str(learning_rate),
        " trainable weights:",
        len(model.trainable_weights),
    )

    model.compile(
        loss="binary_crossentropy",
        optimizer=optimizers.SGD(learning_rate=learning_rate, momentum=0.9),
        metrics=["acc", recall_m, f2_m],
    )

    tijdenVorigePunt = geeft_voortgangs_informatie("Model ingeladen", tijdenVorigePunt)
    history = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,  # 30,
        validation_data=validation_generator,
        validation_steps=validation_steps,
        callbacks=[checkpoint],
    )
    historyList.append(history.history)
    tijdenVorigePunt = geeft_voortgangs_informatie("Na fit", tijdenVorigePunt)
    del model
    gc.collect()
    model = models.load_model(
        modelPath,
        custom_objects={"recall_m": recall_m, "precision_m": precision_m, "f2_m": f2_m},
    )

tijdenVorigePunt = geeft_voortgangs_informatie("Totaal ", tijdenVorigePunt)
for i in sequences:
    plotLossAndAcc(history=historyList[i])
