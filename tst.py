import os
import gc
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import applications
from tensorflow.keras.callbacks import ModelCheckpoint
from generiekeFuncties.presentationFunctions import plotLossAndAcc
from generiekeFuncties.plaatjesFuncties import get_target_picture_size
from generiekeFuncties.utilities import geeftVoortgangsInformatie, initializeerVoortgangsInformatie

modelPath = os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                          'BesteModellen/besteModelResnetV2')
base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
imageSize = get_target_picture_size()
batchSize = 16
sequences = range(3)
epochs_list = [20, 20, 20]
images_per_epoch_list = [3000, 4000, 3000]
aantal_lerende_lagen_conv_base_list = [0, 10, 20]
validation_images = 1500
start_Learning_rate_factor_list = [1, 0.7, 0.5]
initial_start_learning_rate = 0.0035

bestaandmodel_verder_brengen = False

start_Learning_rate_list = [initial_start_learning_rate * i for i in start_Learning_rate_factor_list]
validation_steps = validation_images // batchSize + 1
tijdenVorigePunt = initializeerVoortgangsInformatie("start")
train_datagen = ImageDataGenerator(
    preprocessing_function=applications.inception_resnet_v2.preprocess_input,
    horizontal_flip=True
)

# Note that the validation data should not be augmented!
test_datagen = ImageDataGenerator(preprocessing_function=applications.inception_resnet_v2.preprocess_input)

train_generator = train_datagen.flow_from_directory(
    # This is the target directory
    train_dir,
    # All images will be resized to 150x150
    target_size=(imageSize, imageSize),
    batch_size=batchSize,
    shuffle=True,
    # Since we use binary_crossentropy loss, we need binary labels
    class_mode='binary')

validation_generator = test_datagen.flow_from_directory(
    validation_dir,
    target_size=(imageSize, imageSize),
    batch_size=batchSize,
    shuffle=True,
    class_mode='binary')


def zet_lagen_open_van_conv_base(model_in, aantal):
    print('trainable weights van: ', len(model_in.trainable_weights))
    if aantal == 0:
        model_in.layers[0].trainable = False
        print('naar: ', len(model_in.trainable_weights))
        return model_in
    for layer in model_in.layers:
        layer.trainable = True
    for layer in model_in.layers[0].layers[:-aantal]:
        layer.trainable = False
    for layer in model_in.layers[0].layers[-aantal:]:
        layer.trainable = True
    print('naar: ', len(model.trainable_weights))
    return model_in


if bestaandmodel_verder_brengen:
    model = models.load_model(modelPath)
    print("bestaand model geladen. Trainable weights = ", str(len(model.trainable_weights)))
else:
    conv_base = applications.InceptionResNetV2(include_top=False,
                                               weights='imagenet',
                                               input_shape=(imageSize, imageSize, 3))
    model = models.Sequential()
    model.add(conv_base)
    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    print('This is the number of trainable weights before freezing the conv base:', len(model.trainable_weights))
    conv_base.trainable = False
    #for layer in conv_base.layers[:-2]:
    #    layer.trainable = False
    print('This is the number of trainable weights after freezing the conv base:', len(model.trainable_weights))



checkpoint = ModelCheckpoint(modelPath, monitor='val_acc', verbose=1,
                             save_best_only=True,
                             save_weights_only=False, mode='auto', period=1)
historyList = []

for i in sequences:
    steps_per_epoch = images_per_epoch_list[i] // batchSize + 1
    epochs = epochs_list[i]
    learning_rate = start_Learning_rate_list[i]
    print('##########################################################################')
    print('sequence: ', str(i), ' epochs: ', epochs, ' start lr: ', str(learning_rate))

    model.compile(loss='binary_crossentropy',
                  optimizer=optimizers.SGD(learning_rate=learning_rate, momentum=0.9),
                  metrics=['acc'])

    tijdenVorigePunt = geeftVoortgangsInformatie("Model ingeladen", tijdenVorigePunt)
    history = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,#30,
        validation_data=validation_generator,
        validation_steps=validation_steps,
        callbacks=[checkpoint])
    historyList.append(history)
    tijdenVorigePunt = geeftVoortgangsInformatie("Na fit", tijdenVorigePunt)
    del(model)
    gc.collect()
    model = models.load_model(modelPath)

tijdenVorigePunt = geeftVoortgangsInformatie("Totaal ", tijdenVorigePunt)
for i in sequences:
    plotLossAndAcc(history=historyList[i])