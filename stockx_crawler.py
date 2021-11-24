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

def get_popular_size_info(informacion_ventas):
    most_popular_sizes = [9.0,9.5,10.0,10.5,11.0,11.5,12.0]
    count_of_sales = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    size_info = {}

    for size in most_popular_sizes:
        size_info.update({size:0})


    print(informacion_ventas)
    for venta in informacion_ventas:
        if float(venta["Size"]) in most_popular_sizes:
            index = most_popular_sizes.index(float(venta["Size"]))
            count_of_sales[index] += 1
            acum = float(size_info[float(venta["Size"])])
            acum += float(venta["Sale Price"][1:])
            size_info.update({float(venta["Size"]):acum})
    for index,number_sales in enumerate(count_of_sales):
        if number_sales > 0:
            talla = most_popular_sizes[index]
            recaudado = size_info[talla]
            size_info.update({talla:recaudado/number_sales})
    return size_info

def print_famous_sizes(lista_tallas):
    string_final = ""
    for talla in lista_tallas:
        string_final += "Talla: {0} Precio medio de venta: {1}\n".format(talla,lista_tallas[talla])
    return string_final


def concurrent_search(nombre_de_producto):  
    driver = inicializar_buscador()
    entrypoint = 'https://stockx.com/search?s='+nombre_de_producto
    time.sleep(2)
    driver.get(entrypoint)  
    aceptar_cookies(driver)
    time.sleep(4)

    zapatilla_buscada =  WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'product-ti')]")))

    zapatilla_buscada[0].click()
    time.sleep(4)
    informacion_ventas = obtain_sales_history(driver)
    #print("INFOMARCOIN VENTAS {0} : {1}".format(nombre_de_producto,informacion_ventas))
    popular_size_info = get_popular_size_info(informacion_ventas)
    print("Total gastao: ",obtain_money_spent_on_shoe(informacion_ventas))
    la_zapa = {}
    la_zapa.update({"Nombre":nombre_de_producto,"Total gastado":obtain_money_spent_on_shoe(informacion_ventas),"Media":obtain_money_spent_on_shoe(informacion_ventas)/len(informacion_ventas),"Popular Size":popular_size_info})
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
    precios = [precio["Precio"].strip("\u202f€")  for precio in zapatillas_disponibles if "Colección" not in precio["Nombre"]]
    print("_________________________________________________________ MONGODB PRECIOS")
    print(precios)
    print("_________________________________________________________ COMPARACION PRECIOS")
    for item in lista_stockx:
        for nike in zapatillas_disponibles:
            if item["Nombre"] == nike["Nombre"]:
                print("El precio de la zapatilla {0} nike es {1} y el precio medio de stockx es {2}. \nLos precios de las zapatillas mas cotizadas son: {3}\n\n".format(nike["Nombre"],nike["Precio"],item["Media"],print_famous_sizes(item["Popular Size"])))
                break
 
if "__main__" == __name__:
    lista_stockx = []
    lista_nombres_disponibles = []
    main()

