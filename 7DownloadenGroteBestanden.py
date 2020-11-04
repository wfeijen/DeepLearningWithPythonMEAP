from selenium import webdriver
import time
import regex
from generiekeFuncties.plaatjesFuncties import download_image_naar_memory

patroon_verwijzing_plaatje = r'href=\"(https[^\"]*)\" title'

browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
browser.get("https://imx.to/i/20dl8j")
time.sleep(2)
doc = browser.find_elements_by_xpath('//body/div/span/form/input')
if len(doc) > 0 : doc = doc[0]
doc.click()
time.sleep(2)
match = regex.findall(patroon_verwijzing_plaatje, browser.page_source, regex.IGNORECASE)
if len(match) > 0:
    verwijzing = match[0]
    img = download_image_naar_memory(verwijzing)