from random import random
import numpy as np
from lxml.html import tostring
from selenium.webdriver.chrome.service import Service
from selenium import webdriver 
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from fp.fp import FreeProxy
import json
from concurrent import futures
import pymongo
from fake_useragent import UserAgent

import undetected_chromedriver as uc

class Spoofer(object):

    def __init__(self, country_id=['US','EU','CL'], rand=True, anonym=True):
        self.country_id = country_id
        self.rand = rand
        self.anonym = anonym
        self.userAgent, self.ip = self.get()

    def get(self):
        ua = UserAgent()
        
        proxy = FreeProxy(country_id=self.country_id, rand=self.rand, anonym=self.anonym).get()
        print("COUNTRY_ID ",self.country_id)
        ip = proxy.split("://")[1]
        return ua.random, ip

def aceptar_cookies(driver):
    try:
        #accept_cookies =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//footer[contains(@class,'chakra-modal')]//button")))
        #accept_cookies.click()
        location = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//section[@role = 'dialog']/button[@aria-label = 'Close']")))
        accept_cookies =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'onetrust-banner')]//button[contains(@class,'onetrust-close')]")))
        accept_cookies.click()
        time.sleep(2)
        location.click()
    except TimeoutException:
        driver.refresh()
        time.sleep(4)
        #accept_cookies =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//footer[contains(@class,'chakra-modal')]//button")))
        #accept_cookies.click()
        location = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//section[@role = 'dialog']/button[@aria-label = 'Close']")))
        accept_cookies =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'onetrust-banner')]//button[contains(@class,'onetrust-close')]")))
        accept_cookies.click()
        time.sleep(2)
        location.click()

def inicializar_buscador():
    
    s = Service('/home/santos/Escritorio/chromedriver_linux64/chromedriver')
    options = webdriver.ChromeOptions()
    #options.add_argument("--disable-gpu")
    #options.add_argument('--no-sandbox')

    options.add_argument('--start-maximized')
    
    #options.add_argument('--single-process')
    #options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features")
    options.add_argument('--disable-blink-features=AutomationControlled')
    #options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--enable-javascript")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-infobars")
    

    #options.add_argument('User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3')
    driver = webdriver.Chrome(options=options,service=s)
    #driver.delete_all_cookies()
  
    return driver

def obtain_sales_history(driver):
    all_sales_button = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@data-component,'MarketActivityDrawer')]//button")))
    el_boton = [x for x in all_sales_button if x.text == 'View Sales'][0]
    el_boton.click()
    time.sleep(10)
    try:
        todas_las_ventas = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//tbody[@role = 'rowgroup']//tr")))
        columnas_ventas = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//table[@role = 'table']//thead")))
        columnas_ventas = columnas_ventas.text.split("\n")

        informacion_ventas = []
        for venta in todas_las_ventas:
            la_venta = venta.text.split("\n")
            aux = {}
            for indice,datos in enumerate(la_venta):
                aux.update({columnas_ventas[indice]:datos})
            informacion_ventas.append(aux)    
    except TimeoutException:
        informacion_ventas = []
        aux = {}
        aux.update({"Error":"Error"})
        informacion_ventas.append(aux)    

    return informacion_ventas

def obtain_money_spent_on_shoe(informacion_ventas):
    return sum(list(map(lambda x: int(x["Sale Price"][1:]),informacion_ventas)))

def obtain_shoes_from_mongo(myclient):
    mydb = myclient["nike"]
    mycol = mydb["zapas_nike"]

    query_zapatillas_disponibles = { "State": "Comprar" }
    #query_zapatillas_disponibles = { "State": {"$ne":"Comprar"} }
    zapatillasdisponibles = mycol.find(query_zapatillas_disponibles,{"_id":0,"Nombre":1,"Precio":2})
    zapatillasdisponibles = list(zapatillasdisponibles)
    lista_nombres_disponibles = [x["Nombre"] for x in zapatillasdisponibles if "Colección" not in x["Nombre"]]

    return zapatillasdisponibles,lista_nombres_disponibles

def get_popular_size_info(informacion_ventas):
    most_popular_sizes = [9.0,9.5,10.0,10.5,11.0,11.5,12.0]
    count_of_sales = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    max_of_sales = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    size_info = {}

    for size in most_popular_sizes:
        size_info.update({size:0})

    for venta in informacion_ventas:
        if("W" in venta["Size"]):
            venta["Size"] = venta["Size"][:-1]
        if float(venta["Size"]) in most_popular_sizes and "Error" not in venta["Size"]:
            index = most_popular_sizes.index(float(venta["Size"]))
            count_of_sales[index] += 1
            if(float(venta["Sale Price"][1:]) > max_of_sales[index]):
                max_of_sales[index] = float(venta["Sale Price"][1:])
            acum = float(size_info[float(venta["Size"])])
            acum += float(venta["Sale Price"][1:])
            size_info.update({float(venta["Size"]):acum})

    for index,number_sales in enumerate(count_of_sales):
        if number_sales > 0:
            talla = most_popular_sizes[index]
            recaudado = size_info[talla]
            maximo = max_of_sales[index]
            size_info_aux = {}
            size_info_aux.update({"Media recaudada":recaudado/number_sales})
            size_info_aux.update({"Max sale":maximo})
            size_info_aux.update({"Total ventas":number_sales})
            size_info[talla] = size_info_aux
    return size_info

def print_famous_sizes(lista_tallas):
    string_final = ""
    for talla,datos in lista_tallas.items():
        if datos:
            string_final += "Talla: {0} | Precio medio de venta: {1} | Precio maximo de venta: {2} | Total de ventas: {3}\n".format(talla,str(datos["Media recaudada"]),str(datos["Max sale"]),str(datos["Total ventas"]))
    return string_final


def concurrent_search(nombre_de_producto):  
    driver = inicializar_buscador()
    driver.get('https://stockx.com') 
    time.sleep(5)
    #driver.get(entrypoint)
    #time.sleep(2)
    print("puedo aceptar cookies?")
    aceptar_cookies(driver)

    for queden_nombres in nombre_de_producto:
        print("????? Probando con: ",queden_nombres)
        entrypoint = 'https://stockx.com/search?s='+queden_nombres
        time.sleep(2)
        driver.get(entrypoint)  
        time.sleep(5)

        time.sleep(4)
        print("Buscando")
        zapatilla_buscada =  WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'ProductTile')]//a[contains(@data-testid,'Link')]")))
        print("ola?",len(zapatilla_buscada))
        
        zapatilla_buscada[0].click()
        time.sleep(6)
        informacion_ventas = obtain_sales_history(driver)
        popular_size_info = get_popular_size_info(informacion_ventas)
        la_zapa = {}
        la_zapa.update({"_id":queden_nombres,"Nombre":queden_nombres,"Total gastado":obtain_money_spent_on_shoe(informacion_ventas),"Media":obtain_money_spent_on_shoe(informacion_ventas)/len(informacion_ventas),"Popular Size":popular_size_info})
        lista_stockx.append(la_zapa)
        print("LA ZAPA??",la_zapa)


def concurrent_search2(nombre_de_producto):  
    driver = inicializar_buscador()
    entrypoint = nombre_de_producto
    time.sleep(2)
    driver.get(entrypoint)  
    time.sleep(5)
    driver.get(entrypoint)
    time.sleep(2)
    print("puedo aceptar cookies?")
    aceptar_cookies(driver)
    time.sleep(4)
    print("Buscando")
    
    time.sleep(4)
    '''
    informacion_ventas = obtain_sales_history(driver)
    popular_size_info = get_popular_size_info(informacion_ventas)
    la_zapa = {}
    la_zapa.update({"_id":nombre_de_producto,"Nombre":nombre_de_producto,"Total gastado":obtain_money_spent_on_shoe(informacion_ventas),"Media":obtain_money_spent_on_shoe(informacion_ventas)/len(informacion_ventas),"Popular Size":popular_size_info})
    lista_stockx.append(la_zapa)
    print("LA ZAPA??",la_zapa)
    '''
    
    #driver.quit()

def main():
    myclient = pymongo.MongoClient(
            'mongodb://localhost:27017/',
            username='root',
            password='example')
    zapatillas_disponibles,lista_nombres_disponibles = obtain_shoes_from_mongo(myclient)

    with futures.ThreadPoolExecutor() as executor: #default/optimized number of threads
        executor.map(concurrent_search, lista_nombres_disponibles)

    #chunks = np.array_split(lista_nombres_disponibles, 6)
    #print("LECHUNKS: ",chunks)


    #with futures.ThreadPoolExecutor(max_workers=6) as executor:
    #    executor.map(concurrent_search, [chunk for chunk in chunks])

    #with futures.ThreadPoolExecutor(max_workers=4) as executor:
    #    executor.map(concurrent_search,lista_nombres_disponibles)
    #concurrent_search(lista_nombres_disponibles)


    print("_________________________________________________________ STOCKX")
    print(lista_stockx)
    print("_________________________________________________________ MONGODB")
    print(zapatillas_disponibles)
    precios = [precio["Precio"].strip("\u202f€") for precio in zapatillas_disponibles if "Colección" not in precio["Nombre"]]
    print("_________________________________________________________ MONGODB PRECIOS")
    print(precios)
    print("_________________________________________________________ COMPARACION PRECIOS")
    for item in lista_stockx:
        for nike in zapatillas_disponibles:
            if item["Nombre"] == nike["Nombre"]:
                print("El precio de la zapatilla {0} nike es {1} y el precio medio de stockx es {2}. \nLos precios de las zapatillas mas cotizadas son: {3}\n\n".format(nike["Nombre"],nike["Precio"],item["Media"],print_famous_sizes(item["Popular Size"])))
                break
    


    json_collection = json.loads(json.dumps(lista_stockx))
    print("JSON_COLLECTION",json_collection)
    mydb = myclient["nike"]
    mycol = mydb["zapas_stockx"]
    mycol.insert_many(json_collection)

if "__main__" == __name__:
    lista_stockx = []
    lista_nombres_disponibles = []
    lista_urls = []
    #concurrent_search2("https://stockx.com/")
    main()
    
    '''driver = inicializar_buscador()
    
    
    entrypoint = 'https://stockx.com/search?s=Air Max 95 Khaki and Total Orange'
    
    driver.get(entrypoint) 
    time.sleep(6) 
    aceptar_cookies(driver)'''
    


