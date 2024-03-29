from keras import backend as K
from math import sqrt
from random import random


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
    print('naar: ', len(model_in.trainable_weights))
    return model_in

def zet_random_lagen_open_van_conv_base(model_in, aantal):
    print('trainable weights van: ', len(model_in.trainable_weights))
    if aantal == 0:
        model_in.layers[0].trainable = False
        print('naar: ', len(model_in.trainable_weights))
        return model_in

    for layer in model_in.layers:
        layer.trainable = True
    maxLayerNr = len(model_in.layers[0].layers) - 1
    for layer in model_in.layers[0].layers:
        layer.trainable = False
    for i in range(aantal):
        dobbelsteen = random()
        layerNr = maxLayerNr - int(dobbelsteen * dobbelsteen * maxLayerNr)
        print("Layer open: ", str(layerNr))
        model_in.layers[0].layers[layerNr].trainable = True
    print('naar: ', len(model_in.trainable_weights))
    return model_in

def zet_bovenste_lagen_open_van_conv_base(model_in, aantal_lagen_open):
    print('trainable weights van: ', len(model_in.trainable_weights))
    if aantal_lagen_open == 0:
        model_in.layers[0].trainable = False
        print('naar: ', len(model_in.trainable_weights))
        return model_in
    # Open zetten alle toplayers
    for layer in model_in.layers:
        layer.trainable = True
    # Dichtzetten layers onder layer[0] zodat er aantal layers open blijven
    aantal_lagen_dicht = len(model_in.layers[0].layers) - aantal_lagen_open
    for layer in model_in.layers[0].layers[:aantal_lagen_dicht]:
        layer.trainable = False
        print("Layer dicht: ", str(layer))
    print('naar: ', len(model_in.trainable_weights))
    print('waarvan ', len(model_in.layers[0].trainable_weights), ' in transfer model.')
    return model_in

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true, 0, 1)) * y_pred)
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true, 0, 1)) * y_pred)
    predicted_positives = K.sum(y_pred)
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f2_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 3 * ((precision * recall) / ((2 * precision) + recall + K.epsilon()))


# def recall_m(y_true, y_pred):
#     true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
#     possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
#     recall = true_positives / (possible_positives + K.epsilon())
#     return recall
#
# def precision_m(y_true, y_pred):
#     true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
#     predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
#     precision = true_positives / (predicted_positives + K.epsilon())
#     return precision
#
# def f2_m(y_true, y_pred):
#     precision = precision_m(y_true, y_pred)
#     recall = recall_m(y_true, y_pred)
#     return 3 * ((precision * recall) / (precision+(2 * recall) + K.epsilon()))
