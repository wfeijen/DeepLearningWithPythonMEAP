import os
import sys
import regex
from tkinter import ttk, Tk, CENTER, DISABLED, NORMAL
from selenium import webdriver


class QueryResultaatScherm:
    def __init__(self, query_url, webDriver):
        self.query_url = query_url

        self.root = Tk()
        self.root.title("query resultaten voorbereiden")
        self.start_btn = ttk.Button(self.root, text="start de query", command=self.open_scherm)
        self.start_btn .place(x=0, y=0)
        self.interactie_compleet_btn = ttk.Button(self.root, text="interactie is klaar", command=self.afronden)
        self.interactie_compleet_btn.place(x=0, y=30)
        self.interactie_compleet_btn["state"] = DISABLED
        self.gevonden_verwijzingen_naar_plaatjes = None
        self.driver = webDriver
        self.driverHandle = self.driver.current_window_handle
        self.driver.minimize_window()
        self.root.mainloop()

    def open_scherm(self):
        self.start_btn["state"] = DISABLED
        self.driver.get(self.query_url)
        self.driver.switch_to.window(self.driverHandle)
        self.driver.set_window_rect(0, 0)
        self.interactie_compleet_btn["state"] = NORMAL
        print("####################################################################################")

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
        page_query_resultaat = self.driver.page_source
        self.gevonden_verwijzingen_naar_plaatjes = regex.findall(regex_plaatje, page_query_resultaat, regex.IGNORECASE)
        self.root.destroy()

