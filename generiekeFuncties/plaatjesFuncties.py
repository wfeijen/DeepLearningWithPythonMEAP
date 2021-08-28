import math
import os
from PIL import Image, ImageStat
from send2trash import send2trash
from keras import preprocessing
import numpy as np
import requests
from io import BytesIO
import imagehash
from tensorflow.keras import applications

constHash_size = 6
constBigHash_size = 16


def hashPicture(img):
    try:
        return str(imagehash.phash(img, hash_size=constHash_size))
    except OSError as err:
        print('probleem met hashen: ', err)
        return ''

def bigHashPicture(img):
    try:
        return str(imagehash.phash(img, hash_size=constBigHash_size))
    except OSError as err:
        print('probleem met big hashen: ', err)
        return ''



def hash_size():
    return constHash_size


def bigHash_size():
    return constBigHash_size


def get_target_picture_size():
    return 299


def resize_image(im, vergrotingsfactor):
    sx, sy = im.size
    sx = int(sx * vergrotingsfactor)
    sy = int(sy * vergrotingsfactor)
    return im.resize(size=(sx, sy), resample=Image.BICUBIC)


def convert_image_to_square(im, targetsize_im):
    #try:
        im = im.convert("RGB")
        size_x, size_y = im.size
        mean_color = tuple([math.floor(n) for n in ImageStat.Stat(im)._getmean()])
        antwoord = Image.new(mode="RGB", size=(targetsize_im, targetsize_im), color=mean_color)
        # Breder of vierkant voegen we in de breedte  in het frame
        if size_x >= size_y:  # (en sx <= 2* sy)
            im = resize_image(im, targetsize_im / size_x)
            sx, sy = im.size
            antwoord.paste(im, (0, (targetsize_im - sy) // 2))
            return antwoord
        # Blijft nog over: hoger voegen we in de hoogte in het frame
        im = resize_image(im, targetsize_im / size_y)
        sx, sy = im.size
        antwoord.paste(im, ((targetsize_im - sx) // 2, 0))
    # except :
    #     antwoord = Image.new(mode="RGB", size=(targetsize_im, targetsize_im), color=(0, 0, 0))
        return antwoord

def classificeer_vollig_image(img, kenmerk, classifier_in, image_size_in):
    try:
        img = convert_image_to_square(img, image_size_in)
        pp_image = preprocessing.image.img_to_array(img)
        np_image = np.array(pp_image)
        np_image = np.expand_dims(np.array(np_image).astype(float), axis=0)
        # np_image /= 255.0
        np_image = applications.inception_resnet_v2.preprocess_input(np_image)
        classifications = classifier_in.predict(np_image)
        return classifications[0][0]
    except ValueError as e:
        print('###', kenmerk, ' niet goed verwerkt:', e)
        return -1


def classificeer_vollig_image_from_file(file_name_in, classifier_in, image_size_in):
    img = Image.open(file_name_in)
    return classificeer_vollig_image(img, file_name_in, classifier_in, image_size_in)


def sla_image_op(img, doellocatie):
    try:
        img.save(doellocatie)
        return True
    except IOError as e:
        print("Image niet op te slaan: ", doellocatie, " - ", e)
        return False


def download_image_naar_memory(url_in):
    try:
        response = requests.get(url_in)
    except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError, requests.exceptions.TooManyRedirects) as e:
        print("Communicatie fout in: ", url_in, " - ", e)
        return None
    try:
        img = Image.open(BytesIO(response.content))
    except IOError as e:
        print("Image corrupt: ", url_in, " - ", e)
        return None
    return img
