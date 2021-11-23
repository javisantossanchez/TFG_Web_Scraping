from selenium.webdriver.chrome.service import Service
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from concurrent import futures
import pymongo

def aceptar_cookies(driver):
    accept_cookies =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//footer[contains(@class,'chakra-modal')]//button")))
    accept_cookies.click()

def inicializar_buscador():
    s = Service('/home/santos/Escritorio/chromedriver_linux64/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options,service=s)
    return driver

def obtain_sales_history(driver):
    all_sales_button = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@data-component,'MarketActivityDrawer')]//button")))
    el_boton = [x for x in all_sales_button if x.text == 'View Sales'][0]

    el_boton.click()
    time.sleep(4)
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

    los_euros = obtain_money_spent_on_shoe(informacion_ventas)
    #print("LOSEUROS:",los_euros)
    return informacion_ventas

def obtain_money_spent_on_shoe(informacion_ventas):
    return sum(list(map(lambda x: int(x["Sale Price"][1:]),informacion_ventas)))

def obtain_shoes_from_mongo(myclient):
    mydb = myclient["nike"]
    mycol = mydb["zapas_nike"]

    query_zapatillas_disponibles = { "State": "Comprar" }

    zapatillasdisponibles = mycol.find(query_zapatillas_disponibles,{"_id":0,"Nombre":1,"Precio":2})
    zapatillasdisponibles = list(zapatillasdisponibles)
    lista_nombres_disponibles = [x["Nombre"] for x in zapatillasdisponibles if "Colección" not in x["Nombre"]]

    return zapatillasdisponibles,lista_nombres_disponibles

def concurrent_search(nombre_de_producto):  
    driver = inicializar_buscador()
    entrypoint = 'https://stockx.com/search?s='+nombre_de_producto
    time.sleep(2)
    driver.get(entrypoint)  
    aceptar_cookies(driver)
    time.sleep(4)

    zapatilla_buscada =  WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'product-ti')]")))
    #print(zapatilla_buscada[0].text)

    zapatilla_buscada[0].click()
    time.sleep(4)
    informacion_ventas = obtain_sales_history(driver)
    la_zapa = {}
    la_zapa.update({"Nombre":nombre_de_producto,"Total gastado":obtain_money_spent_on_shoe(informacion_ventas),"Media":obtain_money_spent_on_shoe(informacion_ventas)/len(informacion_ventas)})
    lista_stockx.append(la_zapa)

    driver.quit()

def main():
    myclient = pymongo.MongoClient(
            'mongodb://localhost:27017/',
            username='root',
            password='example')
    zapatillas_disponibles,lista_nombres_disponibles = obtain_shoes_from_mongo(myclient)

    with futures.ThreadPoolExecutor() as executor: #default/optimized number of threads
        executor.map(concurrent_search, lista_nombres_disponibles)
    
    print("_________________________________________________________ STOCKX")
    print(lista_stockx)
    print("_________________________________________________________ MONGODB")
    print(zapatillas_disponibles)
    precios = [precio["Precio"] for precio in zapatillas_disponibles]
    print("_________________________________________________________ MONGODB PRECIOS")
    print(precios)

if "__main__" == __name__:
    lista_stockx = []
    lista_nombres_disponibles = []
    main()

