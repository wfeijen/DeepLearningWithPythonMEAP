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

constHash_size = 8
constBigHash_size = constHash_size * 2


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


def get_minimum_size_short_side_image():
    return get_target_picture_size()


def get_maximum_size_short_side_image():
    return 512


def size_image_proper(img):
    size = img.size
    if min(size) < get_minimum_size_short_side_image():
        return None
    size = math.ceil(get_maximum_size_short_side_image() * max(size) / min(size))
    img.thumbnail((size, size), Image.ANTIALIAS)
    im = img.convert('RGB')
    return im


def remove_small_images_and_give_list_of_proper_sized_images(subdir_name, basedir, remove_small_files_from_source):
    data_set_dir = os.path.join(basedir, subdir_name)
    file_names = [f for f in os.listdir(data_set_dir) if os.path.isfile(os.path.join(data_set_dir, f))]
    verwijderd_vanwege_extentie = 0
    verwijderd_vanwege_te_klein = 0
    kleiner_gemaakt = 0
    for file_name in file_names:
        dummy, file_extension = os.path.splitext(file_name)
        full_file_name = os.path.join(data_set_dir, file_name)
        if file_extension != '.jpg' and file_extension != '.jpeg':
            send2trash(full_file_name)
            file_names.remove(file_name)
        else:
            im = Image.open(full_file_name)
            size = im.size
            if min(size) < get_minimum_size_short_side_image():
                if remove_small_files_from_source:
                    send2trash(full_file_name)
                file_names.remove(file_name)
            elif min(size) > get_maximum_size_short_side_image():
                im = size_image_proper(im)
                send2trash(full_file_name)
                im.save(full_file_name)
    return file_names, verwijderd_vanwege_extentie, verwijderd_vanwege_te_klein, kleiner_gemaakt


def resize_image(im, vergrotingsfactor):
    sx, sy = im.size
    sx = int(sx * vergrotingsfactor)
    sy = int(sy * vergrotingsfactor)
    return im.resize(size=(sx, sy), resample=Image.BICUBIC)


def convert_image_to_square(im, targetsize_im):
    im = im.convert("RGB")
    size_x, size_y = im.size
    mean_color = tuple([math.floor(n) for n in ImageStat.Stat(im)._getmean()])
    antwoord = Image.new(mode="RGB", size=(targetsize_im, targetsize_im), color=mean_color)
    # Als plaatje idioot breed is knippen we de zijkanten er af
    if max(size_x, size_y) > 4 * min(size_x, size_y):
        if size_x > size_y:
            nieuwe_breedte = size_y * 4
            im = im.crop(((size_x - nieuwe_breedte) / 2, 0, nieuwe_breedte, size_y))
            size_x = nieuwe_breedte
        else:
            nieuwe_hoogte = size_x * 4
            im = im.crop((0, (size_y - nieuwe_hoogte) / 2, size_x, nieuwe_hoogte))
            size_y = nieuwe_hoogte
    # Als plaatje volledig binnen nieuwe image valt vergroten we het totdat de langste
    # as gelijk is aan targetSizeIm
    if max(size_x, size_y) < targetsize_im:
        im = resize_image(im, targetsize_im / max(size_x, size_y))
        sx, sy = im.size
        antwoord.paste(im, ((targetsize_im - sx) // 2, (targetsize_im - sy) // 2))
        return antwoord
    # Breed plaatje knippen we in twee stukken en plaatsen onder elkaar
    if size_x > size_y * 2:
        im = resize_image(im, targetsize_im / (size_y * 2))
        sx, sy = im.size
        im_crop1 = im.crop((0, 0, targetsize_im, sy))
        im_crop2 = im.crop((sx - targetsize_im, 0, sx, sy))
        antwoord.paste(im_crop1, (0, 0))
        antwoord.paste(im_crop2, (0, targetsize_im // 2))
        return antwoord
    # Hoog plaatje knippen we in twee stukken en plaatsen naast elkaar
    if size_x * 2 < size_y:
        im = resize_image(im, targetsize_im / (size_x * 2))
        sx, sy = im.size
        im_crop1 = im.crop((0, 0, sx, targetsize_im))
        im_crop2 = im.crop((0, sy - targetsize_im, sx, sy))
        antwoord.paste(im_crop1, (0, 0))
        antwoord.paste(im_crop2, (targetsize_im // 2, 0))
        return antwoord
    # Beetje breder of vierkant voegen we in de breedte  in het frame
    if size_x >= size_y:  # (en sx <= 2* sy)
        im = resize_image(im, targetsize_im / size_x)
        sx, sy = im.size
        antwoord.paste(im, (0, (targetsize_im - sy) // 2))
        return antwoord
    # Blijft nog over: beetje hoger voegen we in de hoogte in het frame
    im = resize_image(im, targetsize_im / size_y)
    sx, sy = im.size
    antwoord.paste(im, ((targetsize_im - sx) // 2, 0))
    return antwoord


def convertImageToSquareIm_from_file(imagePath, targetSizeIm):
    # returns a square part of the image sized to target size
    im = Image.open(imagePath)
    x, y = im.size
    return x, y, convert_image_to_square(im=im, targetsize_im=targetSizeIm)

# def get_square_images_from_image(im, targetSizeIm, maximaalVerschilInVerhoudingImages):
#     # returns a square part of the image sized to target size
#     im = im.convert("RGB")
#     sx, sy = im.size
#     antwoord = []
#     # kijken of het plaatje wel groot genoeg is
#     if min(sx, sy) < targetSizeIm:
#         return antwoord
#     # links of boven bij breed of hoog plaatje
#     if sx >= (sy * maximaalVerschilInVerhoudingImages):
#         antwoord.append(im.crop((0, 0, sy, sy)))
#     elif (sx * maximaalVerschilInVerhoudingImages)<= sy:
#         antwoord.append(im.crop((0, 0, sx, sx)))
#     # en altijd het centrum omdat daar meestal de meeste inforamtie is
#     if sx > sy:
#         left = (sx - sy) / 2
#         antwoord.append(im.crop((left, 0, left + sy, sy)))
#     else:
#         top = (sy - sx) / 2
#         antwoord.append(im.crop((0, top, sx, top + sx)))
#     # en rechts of onder bij breed of hoog plaatje
#     if sx >= (sy * maximaalVerschilInVerhoudingImages):
#         left = sx - sy
#         antwoord.append(im.crop((left, 0, left + sy, sy)))
#     elif (sx * maximaalVerschilInVerhoudingImages)<= sy:
#         top = sy - sx
#         antwoord.append(im.crop((0, top, sx, top + sx)))
#     return antwoord

# def get_square_images_from_file(imagePath, targetSizeIm, minimaalVerschilInVerhoudingImages):
#     # returns a square part of the image sized to target size
#     im = Image.open(imagePath)
#     return get_square_images_from_image(im=im, targetSizeIm=targetSizeIm, maximaalVerschilInVerhoudingImages=minimaalVerschilInVerhoudingImages)

def classificeer_vollig_image(img, kenmerk, classifier_in, image_size_in):
    try:
        b, h, img = convert_image_to_square(img, image_size_in)
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


# def classificeer_vollig_image_from_url(url_in, classifier_in, image_size_in):
# img = download_image_naar_memory(url_in)
# if img is None:
#     return -1
# return classificeer_vollig_image(img, url_in, classifier_in, image_size_in)

def sla_image_op(img, doellocatie):
    try:
        img.save(doellocatie)
    except IOError as e:
        print("Image niet op te slaan: ", doellocatie, " - ", e)


def download_image_naar_memory(url_in):
    try:
        response = requests.get(url_in)
    except requests.exceptions.ConnectionError as e:
        print("Communicatie fout in: ", url_in, " - ", e)
        return None
    try:
        img = Image.open(BytesIO(response.content))
    except IOError as e:
        print("Image corrupt: ", url_in, " - ", e)
        return None
    return img
