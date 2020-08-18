import os
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import VGG16
from keras import models
from keras import layers
from keras import optimizers
from keras.callbacks import ModelCheckpoint
from presentationFunctions import plotLossAndAcc

# 0  Uitgangspositie, geen augmentation base frozen 5000                                                  loss: 0.0656 - acc: 0.9775 - val_loss: 0.0623 - val_acc: 0.9660
# 1  Uitgangspositie, geen augmentation base frozen 10000                                                 loss: 0.0840 - acc: 0.9735 - val_loss: 0.0273 - val_acc: 0.9660
# 2  Uitgangspositie, geen augmentation base frozen 10000 verbetering kwal images                         loss: 0.0840 - acc: 0.9735 - val_loss: 0.0273 - val_acc: 0.9660
# 2  Uitgangspositie, geen augmentation base frozen 10000 + images images squared
# 4  Images 140                                                                                           loss: 0.1294 - acc: 0.9575 - val_loss: 0.1339 - val_acc: 0.9530
# 5  featurewise_center=True                                                                              loss: 0.1438 - acc: 0.9445 - val_loss: 0.1620 - val_acc: 0.9460
# 6  featurewise_std_normalization=True                                                                   loss: 0.1261 - acc: 0.9495 - val_loss: 0.1135 - val_acc: 0.9570
# 7  batchsize 20 -> 32                                                                                   loss: 0.1267 - acc: 0.9541 - val_loss: 0.1291 - val_acc: 0.9544
# 8  batchsize 32 -> 16                                                                                   loss: 0.1424 - acc: 0.9484 - val_loss: 0.1341 - val_acc: 0.9563
# 9  featuerewize -> samplewize                                                                           loss: 0.0843 - acc: 0.9669 - val_loss: 0.1966 - val_acc: 0.9287 Heel onrustig en groot verschil tussen training en validatie
# 10 batchsize 16 -> 32                                                                                   loss: 0.0985 - acc: 0.9600 - val_loss: 0.2493 - val_acc: 0.9125 En ook hier sterke overfit
# 11 8 + batchsize 64                                                                                     loss: 0.1108 - acc: 0.9603 - val_loss: 0.1241 - val_acc: 0.9575
# 12 batchsize 128                                                                                        loss: 0.0895 - acc: 0.9686 - val_loss: 0.1182 - val_acc: 0.9565 Begint wel te klagen over geheugen
# 13 batchsize 64                                                                                         loss: 0.1060 - acc: 0.9642 - val_loss: 0.1327 - val_acc: 0.9502
# 14 nieuwe dataset (zou iets moeilijker moeten zijn)                                                     loss: 0.1189 - acc: 0.9547 - val_loss: 0.1449 - val_acc: 0.9495
# 15 omgezet met sequences met elk een eigen learning_rate 3 sequences van 5 epochs                       loss: 0.1501 - acc: 0.9392 - val_loss: 0.1277 - val_acc: 0.9494
# 16 omgezet met sequences met elk een eigen learning_rate 4 sequences van 5 epochs                       loss: 0.0686 - acc: 0.9750 - val_loss: 0.0979 - val_acc: 0.9716
# 17 omgezet met sequences met elk een eigen learning_rate 5 sequences van 5 epochs                       loss: 0.0494 - acc: 0.9833 - val_loss: 0.0629 - val_acc: 0.9806
# 18 omgezet met sequences met elk een eigen learning_rate 6 sequences van 5 epochs (geen verbetering)    loss: 0.0467 - acc: 0.9834 - val_loss: 0.0563 - val_acc: 0.9815
# 19 18 met incrementele lenget epochs 5, 10, 15, 20, 25, 30 (vanaf 3e sequence geen echte verbetering    loss: 0.0231 - acc: 0.9927 - val_loss: 0.0388 - val_acc: 0.9878
# 20 nieuwe dataset       (vanaf 3e sequence geen echte verbetering                                       loss: 0.0372 - acc: 0.9878 - val_loss: 0.0839 - val_acc: 0.9816


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
    rescale=1.0/255.0,
    #samplewise_center=True,
    #samplewise_std_normalization=True,
    featurewise_center=True,
    featurewise_std_normalization=True,
    #rotation_range=40,
    #width_shift_range=0.2,
    #height_shift_range=0.2,
    #shear_range=0.2,
    #zoom_range=0.2,
    #fill_mode='nearest'
    horizontal_flip=True
)

# Note that the validation data should not be augmented!
test_datagen = ImageDataGenerator(rescale=1./255)

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

conv_base = VGG16(weights='imagenet',
                  include_top=False,
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
