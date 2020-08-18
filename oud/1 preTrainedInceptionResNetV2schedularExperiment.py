import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import applications
from tensorflow.keras.callbacks import ModelCheckpoint
from presentationFunctions import plotLossAndAcc

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
# 10 als 6 maar zonder reload model                                                                         loss: 0.1406 - acc: 0.9458 - val_loss: 0.1930 - val_acc: 0.9298
# 10 met optimum weight reload                                                                              loss: 0.1624 - acc: 0.9394 - val_loss: 0.2178 - val_acc: 0.9250
# 11 50 stappen exponentieel: lijkt er op dat er aanvankelijk een lokaal minimum gekozen word               loss: 34.9989 - acc: 0.8061 - val_loss: 0.4770 - val_acc: 0.8953

base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
imageSize = 140
batchSize = 64
# #[0.001, 0.0001, 0.00001, 0.000001]
# sequences = range(0, 9)
# epochs_list = [5, 5, 5, 10, 5, 5, 5, 5, 5, 5]
# start_Learning_rate_list = [0.01, 0.005, 0.002, 0.001, 0.0005, 0.0002, 0.0001, 0.00005, 0.00002, 0.00001]
# decay_rate_list = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
# maximum_exponent_list = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
sequences = range(0, 1)
epochs_list = [50]
start_Learning_rate_list = [0.01]
decay_rate_list = [0.001]
maximum_exponent_list = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

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
    # Since we use binary_crossentropy loss, we need binary labels
    class_mode='binary')

validation_generator = test_datagen.flow_from_directory(
    validation_dir,
    target_size=(imageSize, imageSize),
    batch_size=batchSize,
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

checkpoint = ModelCheckpoint(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                          'BesteModellen/besteModelResnetV2gewichten'), monitor ='val_acc', verbose=1,
                             save_best_only=True,
                             save_weights_only=True,
                             mode='auto',
                             period=1)
historyList = []

for i in sequences:
    epochs = epochs_list[i]
    decay_rate = decay_rate_list[i]
    maximum_exponent = maximum_exponent_list[i]
    start_Learning_rate = start_Learning_rate_list[i]
    print('###############################################################################################################')
    print('sequence: ', str(i), ' epochs: ', epochs, ' start lr: ', str(start_Learning_rate),
          ' decayRate: ', str(decay_rate), ' maximum exponent: ', maximum_exponent, ' eind learning rate: ',
          str(start_Learning_rate * (decay_rate ** maximum_exponent)))
    lr_schedule = optimizers.schedules.ExponentialDecay(
        initial_learning_rate=start_Learning_rate,
        decay_steps=(epochs * batchSize) / maximum_exponent,
        decay_rate=decay_rate,
        staircase=True)

    model.compile(loss='binary_crossentropy', optimizer=optimizers.RMSprop(learning_rate=lr_schedule), metrics=['acc'])

    history = model.fit(
        train_generator,
        steps_per_epoch=100,#100,
        epochs=epochs_list[i],#30,
        validation_data=validation_generator,
        validation_steps=50, #50,
        callbacks=[checkpoint])
    historyList.append(history)

    #model = models.load_model(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
    #                                       'BesteModellen/besteModelResnetV2 2'))
    model.load_weights(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                    '../BesteModellen/besteModelResnetV2 2'))

model.save(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                          'BesteModellen/besteModelResnetV2totaal'))

for i in sequences:
    plotLossAndAcc(history=historyList[i])
