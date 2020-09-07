import os
import gc
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import applications
from tensorflow.keras.callbacks import ModelCheckpoint
from generiekeFuncties.presentationFunctions import plotLossAndAcc
from generiekeFuncties.plaatjesFuncties import getTargetPictureSize
from generiekeFuncties.utilities import geeftVoortgangsInformatie, initializeerVoortgangsInformatie

# 0  Uitgangspositie, geen augmentation base frozen                                                         loss: 0.0104 - acc: 0.9966 - val_loss: 0.0609 - val_acc: 0.9895
# 1  inception_resnet_v2.preprocess_input     (doet nog niet zoveel)                                        loss: 0.0079 - acc: 0.9977 - val_loss: 0.0676 - val_acc: 0.9889
# 2  nieuwe data                                                                                            loss: 0.0152 - acc: 0.9961 - val_loss: 0.0987 - val_acc: 0.9884
# 3  grotere plaatjes 280 door twee stroken naast elkaar met redundant plaatje batach 64 -> 16
#    Hele goede stats maar slechte confusion matrix in de validatie en meer geheugenruimte nodig            loss: 0.0422 - acc: 0.9869 - val_loss: 0.0225 - val_acc: 0.9925
# 4  terug bij 2                                                                                            loss: 0.0348 - acc: 0.9900 - val_loss: 0.1519 - val_acc: 0.9822
# 5  Nieuwe dataset. Groter en onevenwichtig 3:1 wel niet. Doel is byas de goede kant uit
# 6  Weer een nieuwe dataset. Groter en onevenwichtig 3:1 wel niet. Doel is byas de goede kant uit          loss: 0.0400 - acc: 0.9878 - val_loss: 0.1163 - val_acc: 0.9759
# 7  als 6 maar met zca_whitening = True   geen verbetering dus dat draaien we terug                        loss: 0.0261 - acc: 0.9928 - val_loss: 5.4718 - val_acc: 0.9753
# 8  als 6 maar met vertical_flip=True dat geeft een duidelijke verslechtering dus dat draaien we terug     loss: 0.0691 - acc: 0.9750 - val_loss: 0.3277 - val_acc: 0.9594
# 9  als 6                                                                                                  loss: 0.0458 - acc: 0.9858 - val_loss: 136.5276 - val_acc: 0.9588
# 10 als 6 met alleen opslaan van gewichten tussentijds. En overgang naar tensorflow.keras                  loss: 0.1506 - acc: 0.9427 - val_loss: 0.1852 - val_acc: 0.9300
# 11 En nog eens...                                                                                         loss: 0.1555 - acc: 0.9423 - val_loss: 0.2034 - val_acc: 0.9251
# 12 11 zonder tensorflow.                                                                                  loss: 0.1389 - acc: 0.9467 - val_loss: 0.2014 - val_acc: 0.9294
# 13 6                                                                                                      loss: 0.0960 - acc: 0.9780 - val_loss: 1.2037 - val_acc: 0.9540
# 14 13 met tensorflow                                                                                      loss: 0.0921 - acc: 0.9694 - val_loss: 0.1913 - val_acc: 0.9494
# 15 14 zonder reload                                                                                       loss: 0.1348 - acc: 0.9491 - val_loss: 0.1908 - val_acc: 0.9286
# 15                                                                                                        loss: 0.1365 - acc: 0.9517 - val_loss: 0.1914 - val_acc: 0.9302
# 16 7 x vollediger reload zorgt voor 137
# 17 100 Epochs                                                                                             loss: 0.0428 - acc: 0.9850 - val_loss: 1.0267 - val_acc: 0.9669
# 18 100 Epochs, 200 Steps                                                                                  loss: 0.0132 - acc: 0.9962 - val_loss: 0.2155 - val_acc: 0.9841
# 19 nogmaals nadat dataset er op andere manier neergezet is. Zou in principe gelijk moeten zijn            loss: 0.0029 - acc: 0.9991 - val_loss: 133.2310 - val_acc: 0.9919
# 20 19 met grootte plaatjes 120                                                                            loss: 0.0143 - acc: 0.9954 - val_loss: 6.5726 - val_acc: 0.9865
# 21 Na zuivering van de basisplaatjes vierkante plaatjes nog niet gezuivered                                                                                        0.96
# 22 Na zuiveren vierkante plaatjes (zo'n 20000 aan elke kant)                                              ging naar 98.6 einde memory
# 24 (rerun 22 gemist) na veranderen van een paar plaatjes van kant                                         loss: 4.3377e-04 - acc: 0.9999 - val_loss: 0.0823 - val_acc: 0.9877
# 25 einder memory daarna hervat. Nieuwe plaatjes                                                           loss: 0.0017 - acc: 0.9998 - val_loss: 0.1083 - val_acc: 0.9895
# 26 nieuw plaatjes met gecontroleerde plaatjes allemaal toegevoegd                                                                                          val_acc = 0.96
# 27 gecontroleerde plaatjes opnieuw           recall 0.99                                                                                                  val_acc = 0.957

modelPath = os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                          'BesteModellen/besteModelResnetV2')
base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
imageSize = getTargetPictureSize()
batchSize = 16
sequences = range(3)
epochs_list = [10, 20, 30]
steps_per_epoch=200
validation_steps=100
start_Learning_rate_list = [0.001, 0.0001, 0.00001]

startTijd, tijdVorigePunt = initializeerVoortgangsInformatie()
train_datagen = ImageDataGenerator(
    preprocessing_function=applications.inception_resnet_v2.preprocess_input,
    #rotation_range=40,
    #width_shift_range=0.2,
    #height_shift_range=0.2,
    #shear_range=0.2,
    #zoom_range=0.2,
    #fill_mode='nearest',
    #zca_whitening = True,
    #vertical_flip = True,
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

checkpoint = ModelCheckpoint(modelPath, monitor ='val_acc', verbose=1,
                             save_best_only=True,
                             save_weights_only=False, mode='auto', period=1)
historyList = []

for i in sequences:
    epochs = epochs_list[i]
    learning_rate = start_Learning_rate_list[i]
    print('##########################################################################')
    print('sequence: ', str(i), ' epochs: ', epochs, ' start lr: ', str(learning_rate))

    model.compile(loss='binary_crossentropy', optimizer=optimizers.RMSprop(learning_rate=learning_rate), metrics=['acc'])

    tijdVorigePunt = geeftVoortgangsInformatie("Model ingeladen", startTijd, tijdVorigePunt)
    history = model.fit(
        train_generator,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,#30,
        validation_data=validation_generator,
        validation_steps=validation_steps,
        callbacks=[checkpoint])
    historyList.append(history)
    tijdVorigePunt = geeftVoortgangsInformatie("Na fit", startTijd, tijdVorigePunt)
    del(model)
    gc.collect()

    model = models.load_model(modelPath)
    #model.load_weights(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
    #                                       'BesteModellen/besteModelResnetV2'))

#model.save(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
#                                          'BesteModellen/besteModelResnetV2totaalEind'))

tijdVorigePunt = geeftVoortgangsInformatie("Totaal ", startTijd, tijdVorigePunt)
for i in sequences:
    plotLossAndAcc(history=historyList[i])
