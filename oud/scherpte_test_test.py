from generiekeFuncties.plaatjesFuncties import scherpte_maalGrootte_image
from generiekeFuncties.fileHandlingFunctions import dict_values_string_to_int
from PIL import Image
import os

directory = '/media/willem/KleindSSD/machineLearningPictures/take1/testSet/Scherptetest'
schalingsfactor = 2
# Laad plaatje en doe scherptetest
# Origineel
# Verkleind
# Verkleind en grootte origineel
# Verkleind en twee keer grootte origineel

dict = {'a' : '1', 'b' : '2'}
dict2 = dict_values_string_to_int(dict)

print(type(dict2))
def test_scherptes(image_pad, schalingsfactor):
    print(image_pad)
    original_image = Image.open(image_pad)
    original_width, original_height = original_image.size

    # 50%
    klein_image = original_image.resize((original_width // schalingsfactor, original_height // schalingsfactor), Image.Resampling.LANCZOS)
    terug_geschaald_image = klein_image.resize((original_width, original_height), Image.Resampling.LANCZOS)
    groot_image = klein_image.resize((original_width * schalingsfactor, original_height * schalingsfactor), Image.Resampling.LANCZOS)
    origineel_scherpte = scherpte_maalGrootte_image(original_image)
    klein_scherpte = scherpte_maalGrootte_image(klein_image)
    terug_scherpte = scherpte_maalGrootte_image(terug_geschaald_image)
    groot_scherpte = scherpte_maalGrootte_image(groot_image)

    print('origineel: ' + str(origineel_scherpte))
    print('klein: '+ str(klein_scherpte) + " factor: " + str(klein_scherpte / origineel_scherpte))
    print('terug: '+ str(terug_scherpte) + " factor: " + str(terug_scherpte / origineel_scherpte))
    print('groot: '+ str(groot_scherpte) + " factor: " + str(groot_scherpte / origineel_scherpte))

    # Close the original and resized images
    original_image.close()
    klein_image.close()
    terug_geschaald_image.close()
    groot_image.close()

for filename in os.listdir(directory):
    if filename.endswith('.jpg'):
        test_scherptes(os.path.join(directory, filename), schalingsfactor)


