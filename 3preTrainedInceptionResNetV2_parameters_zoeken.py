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
from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasClassifier

# 0                                                                                                    loss: 0.0033 - acc: 0.9992 - val_loss: 1.0476 - val_acc: 0.9831
# 1 Adam lr[0.01, 0.0001, 0.00001] epsilon = 0.1 slecht
# 2 SGD [0.1, 0.01, 0.001] velocity 0.9                                                                  loss: 0.0351 - acc: 0.9914 - val_loss: 0.0779 - val_acc: 0.9742
# 3 SGD [0.01, 0.005, 0.002] velocity 0.9                                                                loss: 0.0035 - acc: 0.9988 - val_loss: 0.0794 - val_acc: 0.9871
# 4 3 en epochs_list = [60]# images_per_epoch_list = [12000]# start_Learning_rate_list = [0.005]         loss: 0.0835 - acc: 0.9653 - val_loss: 0.3899 - val_acc: 0.9290
# De 3 tier aanpak is ook hier weer superieur
# 5 3 images aantal verdubbeld, Maakt blijkbaar geen verschil                                            loss: 0.0321 - acc: 0.9896 - val_loss: 0.0598 - val_acc: 0.9820
# 6 Metrics = Recall

modelPath = os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                          'BesteModellen/besteModelResnetV2')
base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
imageSize = get_target_picture_size()
batchSize = 16
sequences = range(3)
#epochs_list = [20, 20, 30]
epochs_list = [20, 20, 20, 20]
images_per_epoch_list = [2000, 2000, 3000, 5000]
#images_per_epoch_list = [4000, 8000, 12000]
start_Learning_rate_factor_list = [1, 0.5, 0.2, 0.1]
validation_images = 1000

validation_steps = validation_images // batchSize + 1
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


checkpoint = ModelCheckpoint(modelPath, monitor='val_acc', verbose=1,
                             save_best_only=True,
                             save_weights_only=False, mode='auto', period=1)

def createInitialModel():
    new_model = models.Sequential()
    new_model.add(conv_base)
    new_model.add(layers.Flatten())
    new_model.add(layers.Dense(256, activation='relu'))
    new_model.add(layers.Dense(1, activation='sigmoid'))
    return new_model

initial_start_learning_rate = 0.01
historyList = []
def runModel(model, init_start_learning_rate, strt_Learning_rate_factor_list):
    start_learning_rate_list = [init_start_learning_rate * i for i in strt_Learning_rate_factor_list]
    startTijd, tijdVorigePunt = initializeerVoortgangsInformatie()
    for i in sequences:
        steps_per_epoch = images_per_epoch_list[i] // batchSize + 1
        epochs = epochs_list[i]
        learning_rate = start_learning_rate_list[i]
        print('##########################################################################')
        print('sequence: ', str(i), ' epochs: ', epochs, ' start lr: ', str(learning_rate))

        model.compile(loss='binary_crossentropy',
                      optimizer=optimizers.SGD(learning_rate=learning_rate, momentum=0.9),
                      metrics=['acc'])

        tijd_vorige_punt = geeftVoortgangsInformatie("Model ingeladen", startTijd, tijd_vorige_punt)
        history = model.fit(
            train_generator,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,#30,
            validation_data=validation_generator,
            validation_steps=validation_steps,
            callbacks=[checkpoint])
        historyList.append(history)
        tijd_vorige_punt = geeftVoortgangsInformatie("Na fit", startTijd, tijd_vorige_punt)
        del(model)
        gc.collect()
        model = models.load_model(modelPath)

    tijdVorigePunt = geeftVoortgangsInformatie("Totaal ", startTijd, tijdVorigePunt)
for i in sequences:
    plotLossAndAcc(history=historyList[i])

