import os
from keras.preprocessing.image import ImageDataGenerator
from keras import models
from keras import layers
from keras import optimizers
from keras import applications
from keras.callbacks import ModelCheckpoint
from presentationFunctions import plotLossAndAcc

# 0  Uitgangspositie, geen augmentation base frozen                                                       loss: 0.0138 - acc: 0.9961 - val_loss: 0.0806 - val_acc: 0.9883


base_dir = '/mnt/GroteSchijf/machineLearningPictures/werkplaats'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')
imageSize = 140
batchSize = 64
sequences = range(0, 3)
epochs_list = [5, 10, 15, 20]
learning_rate_list = [0.001, 0.0001, 0.00001, 0.000001]

train_datagen = ImageDataGenerator(
    preprocessing_function=applications.xception.preprocess_input,
    #samplewise_center=True,
    #samplewise_std_normalization=True,
    #rotation_range=40,
    #width_shift_range=0.2,
    #height_shift_range=0.2,
    #shear_range=0.2,
    #zoom_range=0.2,
    #fill_mode='nearest'
    horizontal_flip=True
)

# Note that the validation data should not be augmented!
test_datagen = ImageDataGenerator(preprocessing_function=applications.xception.preprocess_input)

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
                                          '../BesteModellen/besteModelResnetV2 2'), monitor ='val_acc', verbose=1,
                             save_best_only=True,
                             save_weights_only=False, mode='auto', period=1)
modelList = []
historyList = []

modelList.append(model)

for i in sequences:
    print('sequence: ', str(i))
    modelList[i].compile(loss='binary_crossentropy',    optimizer=optimizers.RMSprop(learning_rate=learning_rate_list[i]),    metrics=['acc'])

    history = model.fit(
        train_generator,
        steps_per_epoch=100,#100,
        epochs=epochs_list[i],#30,
        validation_data=validation_generator,
        validation_steps=50, #50,
        callbacks=[checkpoint])
    historyList.append(history)

    model = models.load_model(os.path.join('/mnt/GroteSchijf/machineLearningPictures/take1',
                                           '../BesteModellen/besteModelResnetV2 2'))
    modelList.append(model)

for i in sequences:
    plotLossAndAcc(history=historyList[i])
