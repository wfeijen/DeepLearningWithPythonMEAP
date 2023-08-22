import math
import os
from datetime import datetime, timedelta
from PIL import Image, ImageStat, ImageOps
from send2trash import send2trash
import numpy as np
import requests
from io import BytesIO
import imagehash

from requests import exceptions
from generiekeFuncties.fileHandlingFunctions import writeDict




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

def scherpte_maalGrootte_image(im):
    im = ImageOps.grayscale(im)
    sx, sy = im.size
    array = np.asarray(im, dtype=np.int32)
    gy, gx = np.gradient(array)
    g_norm = np.sqrt(gx ** 2 + gy ** 2)
    return int(np.sum(g_norm) / sx) # Merk op dat avg de gemiddelde scherpte geeft. Nu nemen we ook de grootte van de image mee. Precies wat we willen.

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

def sla_image_op(img, doellocatie):
    try:
        img.save(doellocatie)
        return True
    except IOError as e:
        print("Image niet op te slaan: ", doellocatie, " - ", e)
        return False


def download_image_naar_memory(url_in):
    try:
        response = requests.get(url_in, verify=False, timeout=10)
    except (requests.exceptions.ContentDecodingError, requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError, requests.exceptions.TooManyRedirects, requests.exceptions.MissingSchema, requests.exceptions.ReadTimeout) as e:
        print("Communicatie fout - ", e)
        return None
    try:
        img = Image.open(BytesIO(response.content))
    except IOError as e:
        print("Image corrupt - ", e)
        return None
    return img


