import os
import regex

a = "https://imx.to/i/20bygb"

print(os.path.basename(a))
print(os.path.split(a))

match = regex.findall('//([^\.]+)\.', a, regex.IGNORECASE)

print(match)