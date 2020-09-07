import os
import re

camera = "dmc-g7"
directory = os.path.expanduser("~/Pictures/In_bewerking")

# pak alle filenamen uit de directory
file_names = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

# sorteer ze omgekeerd want we tellen er een uur bij op en zo kan er nooit een nieuwe filenaam tijdelijk gelijk worden aan een oude
file_names.sort(reverse=True)
# Goede camera pakken
file_names = [f for f in file_names if camera in f]
# Nieuwe filenaam berekenen en die naast de oude in een dictionary zetten
file_names_mutatie = dict(zip(file_names, [re.sub('(\d{8}_)(\d{2})', lambda x: x.group(1) + str(int(x.group(2)) + 1), f) for f in file_names]))
# Hernoemen voor elke file in de dictionary
for oud, nieuw in file_names_mutatie.items():
    os.rename(os.path.join(directory, oud), os.path.join(directory,nieuw))
