#https://imx.to/i/20dl8j
# <input id="continuebutton" type="submit" name="imgContinue" value="Continue to your image...">

# from selenium import webdriver
# import time
#
# driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
# driver.get('http://codepad.org')
#
# # click radio button
# python_button = driver.find_elements_by_xpath("//input[@name='lang' and @value='Python']")[0]
# python_button.click()
#
# # type text
# text_area = driver.find_element_by_id('textarea')
# text_area.send_keys("print('Hello World')")
#
# # click submit button
# submit_button = driver.find_elements_by_xpath('//*[@id="editor"]/form/table/tbody/tr[3]/td/table/tbody/tr/td/div/table/tbody/tr/td[3]')
# if len(submit_button) > 0: submit_button = submit_button[0]
# submit_button.click()







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
i = 1

