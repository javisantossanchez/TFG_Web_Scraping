from selenium.webdriver.chrome.service import Service
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def aceptar_cookies(driver):
    accept_cookies =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//footer[contains(@class,'chakra-modal')]//button")))
    accept_cookies.click()

entrypoint = 'https://stockx.com/search?s='
zapatilla = 'ACG Mountain Fly GORE-TEX Dark Grey'

#options.headless = True

s = Service('/home/santos/Escritorio/chromedriver_linux64/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options,service=s)

agent = driver.execute_script("return navigator.webdriver")
print(agent)

driver.get(entrypoint+zapatilla)
time.sleep(4)
aceptar_cookies(driver)
time.sleep(4)

zapatilla_buscada =  WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'product-ti')]")))
print(zapatilla_buscada[0].text)

zapatilla_buscada[0].click()
time.sleep(4)

all_sales_button = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@data-component,'MarketActivityDrawer')]//button")))

el_boton = [x for x in all_sales_button if x.text == 'View Sales'][0]


el_boton.click()
time.sleep(4)
todas_las_ventas = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//tbody[@role = 'rowgroup']//tr")))
columnas_ventas = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//table[@role = 'table']//thead")))
columnas_ventas = columnas_ventas.text.split("\n")

for venta in todas_las_ventas:
    la_venta = venta.text.split("\n")
    print(la_venta)

informacion_ventas = []
for venta in todas_las_ventas:
    la_venta = venta.text.split("\n")
    aux = {}
    for indice,datos in enumerate(la_venta):
        aux.update({columnas_ventas[indice]:datos})
    informacion_ventas.append(aux)

print("------------------------------------------------VENTAS DE LA ZAPATILLA------------------------------------------------")
print(informacion_ventas)
total_dinero_zapatilla = 0
for compra in informacion_ventas:
    total_dinero_zapatilla += int(compra["Sale Price"][1:])

print("Total movido: ",total_dinero_zapatilla)
print("Media de la zapatilla: ",total_dinero_zapatilla/len(todas_las_ventas))

