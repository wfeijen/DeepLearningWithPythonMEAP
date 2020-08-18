import os
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import VGG16
from keras import models
from keras import layers
from keras import optimizers
import matplotlib.pyplot as plt

base_dir = '/mnt/GroteSchijf/dogs_vs_cats/smallSelection'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')

conv_base = VGG16(weights='imagenet',
include_top=False,
input_shape=(150, 150, 3))


# loss: 0.1131 - acc: 0.9618 - val_loss: 0.2257 - val_acc: 0.9208

datagen = ImageDataGenerator(rescale=1./255)
batch_size = 40
def extract_features(directory):
    from os import listdir
    from os.path import isfile, join
    dir = directory + "/cats"
    onlyfiles = [f for f in os.listdir(dir) if isfile(join(dir, f))]
    sample_count = (len(onlyfiles) // batch_size) * batch_size

    features = np.zeros(shape=(sample_count, 4, 4, 512))
    labels = np.zeros(shape=(sample_count))
    generator = datagen.flow_from_directory(
        directory,
        target_size=(150, 150),
        batch_size=batch_size,
        class_mode='binary')
    i = 0
    for inputs_batch, labels_batch in generator:
        print("Batchnummer = " + str(i))
        features_batch = conv_base.predict(inputs_batch)
        print("Batchsize = " + str(len(features_batch)))

        features[i * batch_size : (i + 1) * batch_size] = features_batch
        labels[i * batch_size : (i + 1) * batch_size] = labels_batch
        i += 1
        if i * batch_size >= sample_count:
            # Note that since generators yield data indefinitely in a loop,
            # we must `break` after every image has been seen once.
            break
    return features, labels, sample_count
train_features, train_labels, train_count = extract_features(train_dir)
validation_features, validation_labels, validation_count = extract_features(validation_dir)
test_features, test_labels, test_count = extract_features(test_dir)

train_features = np.reshape(train_features, (train_count, 4 * 4 * 512))
validation_features = np.reshape(validation_features, (validation_count, 4 * 4 * 512))
test_features = np.reshape(test_features, (test_count, 4 * 4 * 512))

model = models.Sequential()
model.add(layers.Dense(256, activation='relu', input_dim=4 * 4 * 512))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(1, activation='sigmoid'))
model.compile(optimizer=optimizers.RMSprop(lr=2e-5), loss='binary_crossentropy', metrics=['acc'])
history = model.fit(train_features, train_labels,
    epochs=30,
    batch_size=batch_size,
    validation_data=(validation_features, validation_labels))

acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()
