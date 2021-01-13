import os
import sys
import regex
import time
from tkinter import ttk, Tk, CENTER, DISABLED, NORMAL
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

class QueryResultaatScherm:
    def __init__(self, query_url):
        self.query_url = query_url
        self.start_btn = ttk.Button(self.root, text="start de query", command=self.niet)
        self.start_btn .place(x=0, y=0)
        self.interactie_compleet_btn = ttk.Button(self.root, text="VERWIJDER (^)", command=self.open_scherm)
        self.interactie_compleet_btn.place(x=0, y=30)
        self.interactie_compleet_btn["state"] = DISABLED
        self.gevonden_verwijzingen_naar_plaatjes = None

    def open_scherm(self):
        self.start_btn["state"] = DISABLED
        self.driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver")
        self.driver.get(self.query_url)
        self.interactie_compleet_btn["state"] = NORMAL

    def afronden(self):
        self.interactie_compleet_btn["state"] = DISABLED
        self.driver.minimize_window()
        page_query_resultaat = self.driver.page_source
        regex_plaatje = '(https[^&]+jpg)&'  # '{"url":"([^"]+jpg)"' #{"url":"https://wallpapercave.com/wp/wp6828079.jpg"
        gevonden_verwijzingen_naar_plaatjes = regex.findall(regex_plaatje, page_query_resultaat, regex.IGNORECASE)
        if len(gevonden_verwijzingen_naar_plaatjes) == 0:
            print('Niks gevonden. Blijkbaar zijn we ontdekt 1.')
            self.driver.maximize_window()
            input("Press Enter to continue...")
            page_query_resultaat = self.driver.page_source
            gevonden_verwijzingen_naar_plaatjes = regex.findall(regex_plaatje, page_query_resultaat,
                                                                regex.IGNORECASE)
            if len(gevonden_verwijzingen_naar_plaatjes) == 0:
                print('Niks gevonden. Blijkbaar zijn we ontdekt 2.')
                sys.exit()
        scroll_pause_time = 10
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            print('scroll')
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        page_query_resultaat = self.driver.page_source
        self.gevonden_verwijzingen_naar_plaatjes = regex.findall(regex_plaatje, page_query_resultaat, regex.IGNORECASE)
        self.driver.quit()
