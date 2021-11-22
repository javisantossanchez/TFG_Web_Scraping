import pymongo
import requests
from fpdf import FPDF
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time

def aceptar_cookies(driver):
    accept_cookies =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//footer[contains(@class,'chakra-modal')]//button")))
    accept_cookies.click()
    driver.get_cookies()
    #pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))

entrypoint = 'https://stockx.com/search?s='
zapatilla = 'ACG Mountain Fly GORE-TEX Dark Grey'
#myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myclient = pymongo.MongoClient('mongodb://localhost:27017/',
                  username='root',
                 password='example')
mydb = myclient["nike"]
mycol = mydb["zapas_nike"]

query_zapatillas_disponibles = { "State": "Comprar" }
query_zapatillas_no_disponibles = {"State": {"$ne" : "Comprar"}}

zapatillasdisponibles = mycol.find(query_zapatillas_disponibles,{"_id":0,"Nombre":1})
zapatillasnodisponibles = mycol.find(query_zapatillas_no_disponibles,{"_id":0,"Nombre":1})

lista_nombres_agotados = [x["Nombre"] for x in zapatillasnodisponibles]
lista_nombres_disponibles = [x["Nombre"] for x in zapatillasdisponibles]
print("------------------- Productos disponibles en la BD: -------------------\n{0}".format(lista_nombres_disponibles))
print("------------------- Productos NO disponibles en la BD: -------------------\n{0}".format(lista_nombres_agotados))

options = Options()
#options.headless = True
print("Charging Nike Sneakers page")
driver = webdriver.Firefox(options=options)
driver.get(entrypoint+zapatilla)
agent = driver.execute_script("return navigator.userAgent")
print(agent)
#aceptar_cookies(driver)
#time.sleep(5)
#print(driver.page_source)
