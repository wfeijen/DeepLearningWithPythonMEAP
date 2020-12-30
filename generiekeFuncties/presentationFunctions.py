# Presentatiefuncties voor gebruik met Keras ontwikkeling
from keras.preprocessing import image
import matplotlib.pyplot as plt
import numpy as np


def plotLossAndAcc(history):
    acc = history.history['acc']
    val_acc = history.history['val_acc']
    recall_m = history.history['recall_m']
    val_recall_m = history.history['val_recall_m']
    epochs = range(1, len(acc) + 1)
    plt.plot(epochs, acc, 'bo', label='Training acc')
    plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.legend()
    plt.figure()
    plt.plot(epochs, recall_m, 'bo', label='Training recall_m')
    plt.plot(epochs, val_recall_m, 'b', label='Validation recall_m')
    plt.title('Training and validation recall_m')
    plt.legend()
    plt.show()

def load_image(img_path, show=False):
    img = image.load_img(img_path, target_size=(150, 150))
    img_tensor = image.img_to_array(img)                    # (height, width, channels)
    img_tensor = np.expand_dims(img_tensor, axis=0)         # (1, height, width, channels), add a dimension because the model expects this shape: (batch_size, height, width, channels)
    img_tensor /= 255.                                      # imshow expects values in the range [0, 1]

    if show:
        plt.imshow(img_tensor[0])
        plt.axis('off')
        plt.show()
    return img_tensor