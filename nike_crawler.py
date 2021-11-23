from fpdf import FPDF
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import time
from PIL import Image
from concurrent import futures

class PDF(FPDF):
    def __init__(self,productos_disponibles):
        self.pdf = FPDF()
        self.formatPDF()
        for producto in productos_disponibles:
            self.pdf.add_page()
            self.pdf.set_font("Arial", 'B', size=18)
            self.pdf.set_text_color(0, 51, 69)
            self.pdf.cell(200, 7, txt=producto["Nombre"], ln=1, align="L")
            self.pdf.ln(10)
            self.pdf.set_font("Arial", 'B', size=10)
            self.pdf.set_text_color(0, 51, 69)

            if "precio" in producto:            
                el_precio_del_producto_parseado = producto["Precio"].replace(u"\u202f€","")         
                el_precio_del_producto_parseado = el_precio_del_producto_parseado + chr(128) #SIMBOLO DEL EURO EN ASCII
                self.pdf.cell(200, 4, txt="Precio "+el_precio_del_producto_parseado, ln=1, align="L")
                self.pdf.ln(5)
                          
            cover = Image.open("mongodb/database/imagenes/"+producto["Nombre"]+".png")
            width, height = cover.size
            producto["Imagen"] = "/home/database/imagenes/"+producto["Nombre"]+".png"

            self.pdf.cell(200, 2, txt="Url: "+producto["url"], ln=1, align="L")
            self.pdf.ln(5)
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.set_font("Arial", size=13)
            self.pdf.image("mongodb/database/imagenes/"+producto["Nombre"]+".png", w = width/(3.5), h=height/(3.5))
            self.pdf.footer()

        self.pdf.output("primerpdf.pdf")
        print("IMPRIMIENDO PDF")

    def header(self):
        title = "Zapatillas Disponibles                                                                                            BOT JS47"
        # Arial bold 15
        self.set_font('Arial','I', size=12)
        # Calculate width of title and position
        w = self.get_string_width(title)
        self.set_x((210 - w) / 2)
        self.set_y(15)
        # Colors of frame, background and text

        self.set_text_color(150, 150, 150)
        # Thickness of frame (1 mm)
        # Title
        self.cell(w, 10, title, ln=1, align='C')
        # Line break
        self.ln(10)

    def footer(self):
        if self.page_no() != 1 :
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Text color in gray
            self.set_text_color(128)
            # Page number
            self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def formatPDF(self):
        self.pdf.add_page()
        self.pdf.footer()
        self.pdf.set_font("Arial", 'B', size=28)
        self.pdf.set_text_color(0, 51, 69)
        self.pdf.set_y(80)
        self.pdf.cell(200, 20, txt="Zapatillas", ln=8, align="C")
        self.pdf.set_font("Arial", size=23)
        self.pdf.cell(200, 30, txt="Nike Sneakers", ln=9, align="C")
        self.pdf.set_author("Javier Santos Sánchez")

class NikeShop:
    def __init__(self):
        with futures.ThreadPoolExecutor(max_workers=2) as executor:
            running_tasks = [executor.submit(inicializar_buscador),executor.submit(inicializar_buscador)]
            self.driver = running_tasks[0].result()
            driver2 = running_tasks[1].result()
        start = time.time()
        self.todos_los_productos = inspeccionar_main_page(self.driver,driver2)
        end = time.time()
        print("Tiempo empleado en inspeccionar main_page {0}".format(end - start))
        print("Tenemos estos datos: ",self.todos_los_productos)
        self.driver.quit()
        driver2.quit()

        #self.todos_los_productos = [{'Nombre': 'Air Max BW Lyon ', 'State': 'Notifícame', 'data-qa': 'product-card-1'}, {'Nombre': 'Air Max 1 x Patta Aqua Noise ', 'State': 'Notifícame', 'data-qa': 'product-card-4'}, {'Nombre': 'Air Jordan 14 Low para mujer Shocking Pink ', 'State': 'Notifícame', 'data-qa': 'product-card-8'}, {'Nombre': "Blazer Mid '77 Sequoia Quilt  ", 'State': 'Notifícame', 'data-qa': 'product-card-14'}, {'Nombre': "Blazer Mid '77 Sail Quilt ", 'State': 'Notifícame', 'data-qa': 'product-card-15'}, {'Nombre': 'Air Force 1 Next Nature Brown Kelp ', 'State': 'Notifícame', 'data-qa': 'product-card-16'}, {'Nombre': 'Air Force 1 Toasty ', 'State': 'Notifícame', 'data-qa': 'product-card-17'}, {'Nombre': 'Air Force 1 Winter Premium Summit White ', 'State': 'Producto agotado', 'data-qa': 'product-card-18'}, {'Nombre': 'Air Force 1 x Alyx University Red and Black ', 'State': 'Producto agotado', 'data-qa': 'product-card-20'}, {'Nombre': 'Air Force 1 x Alyx Black and University Red ', 'State': 'Producto agotado', 'data-qa': 'product-card-21'}, {'Nombre': 'LDWaffle x sacai x UNDERCOVER Midnight Spruce and University Red ', 'State': 'Producto agotado', 'data-qa': 'product-card-22'}, {'Nombre': 'LDWaffle x sacai x UNDERCOVER Night Maroon and Team Royal  ', 'State': 'Producto agotado', 'data-qa': 'product-card-23'}, {'Nombre': 'LDWaffle x sacai x UNDERCOVER Black and Bright Citron ', 'State': 'Producto agotado', 'data-qa': 'product-card-24'}, {'Nombre': 'Dunk High para mujer Next Nature Summit White ', 'State': 'Notifícame', 'data-qa': 'product-card-25'}, {'Nombre': 'Air Force 1 para mujer Pecan Quilt ', 'State': 'Notifícame', 'data-qa': 'product-card-26'}, {'Nombre': 'Air Jordan 3 Pine Green ', 'State': 'Producto agotado', 'data-qa': 'product-card-28'}, {'Nombre': 'SB Dunk Low Mummy ', 'State': 'Producto agotado', 'data-qa': 'product-card-29'}, {'Nombre': "Jordan Series .03 Dear '90s ", 'State': 'Comprar', 'data-qa': 'product-card-32', 'url': 'https://www.nike.com/es/launch/t/jordan-series-03-dear-90s'}, {'Nombre': 'Air Force 1 Mid Jewel NYC Cool Grey ', 'State': 'Comprar', 'data-qa': 'product-card-33', 'url': 'https://www.nike.com/es/launch/t/air-force-1-mid-jewel-nyc-cool-grey'}, {'Nombre': 'Air Force 1 Mid Jewel NYC Midnight Navy ', 'State': 'Producto agotado', 'data-qa': 'product-card-34'}, {'Nombre': 'Air Jordan 5 para mujer Bluebird ', 'State': 'Comprar', 'data-qa': 'product-card-35', 'url': 'https://www.nike.com/es/launch/t/womens-air-jordan-5-bluebird'}, {'Nombre': 'BE-DO-WIN Hyper Royal ', 'State': 'Comprar', 'data-qa': 'product-card-36', 'url': 'https://www.nike.com/es/launch/t/be-do-win-hyper-royal'}, {'Nombre': 'Air Max BW Persian Violet ', 'State': 'Producto agotado', 'data-qa': 'product-card-42'}, {'Nombre': 'NOCTA Golf Colección de ropa ', 'State': 'Producto agotado', 'data-qa': 'product-card-45'}, {'Nombre': 'Air Jordan 11 Low IE Bred ', 'State': 'Comprar', 'data-qa': 'product-card-48', 'url': 'https://www.nike.com/es/launch/t/air-jordan-11-low-ie-bred'}, {'Nombre': 'Free Run 2 Pure Platinum ', 'State': 'Comprar', 'data-qa': 'product-card-50', 'url': 'https://www.nike.com/es/launch/t/free-run-2-pure-platinum'}, {'Nombre': 'Air Huarache Toadstool ', 'State': 'Comprar', 'data-qa': 'product-card-52', 'url': 'https://www.nike.com/es/launch/t/air-huarache-toadstool'}, {'Nombre': 'Producto agotado', 'State': 'Producto agotado', 'data-qa': 'product-card-53'}, {'Nombre': 'SB Dunk High Gundam ', 'State': 'Producto agotado', 'data-qa': 'product-card-54'}, {'Nombre': 'Air Jordan 1 Prototype ', 'State': 'Producto agotado', 'data-qa': 'product-card-55'}, {'Nombre': 'Free Run 2 Black and White ', 'State': 'Comprar', 'data-qa': 'product-card-56', 'url': 'https://www.nike.com/es/launch/t/free-run-2-black-white'}, {'Nombre': 'Air Jordan 13 Obsidian ', 'State': 'Comprar', 'data-qa': 'product-card-57', 'url': 'https://www.nike.com/es/launch/t/air-jordan-13-obsidian1'}, {'Nombre': 'Free Run Trail Thunder Blue ', 'State': 'Comprar', 'data-qa': 'product-card-58', 'url': 'https://www.nike.com/es/launch/t/free-run-trail-thunder-blue'}, {'Nombre': 'Air Jordan 5 Moonlight ', 'State': 'Producto agotado', 'data-qa': 'product-card-60'}, {'Nombre': 'Dunk High Up para mujer Varsity Maize ', 'State': 'Producto agotado', 'data-qa': 'product-card-61'}, {'Nombre': 'Air Force 1 Jewels ', 'State': 'Producto agotado', 'data-qa': 'product-card-62'}, {'Nombre': 'Air Jordan 14 Low para mujer Iconic Red ', 'State': 'Comprar', 'data-qa': 'product-card-64', 'url': 'https://www.nike.com/es/launch/t/womens-air-jordan-14-low-iconic-red1'}]


def inicializar_buscador():
    options = Options()
    #options.headless = True
    print("Charging Nike Sneakers page")
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.nike.com/es/launch")
    aceptar_cookies(driver)
    load_more_botton = scroll_to_bottom(driver)
    load_more_botton.click()
    time.sleep(2)
    return driver

def scroll_to_bottom(driver):
    load_more_button =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//section[contains(@class,'load-more')]//button")))
    return load_more_button

def scroll_shim(passed_in_driver, object):
    x = object.location['x']
    y = object.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    passed_in_driver.execute_script(scroll_by_coord)
    passed_in_driver.execute_script(scroll_nav_out_of_way)

def buscar_todos_los_productos(driver):
    all_products = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'product-card')]")))
    return all_products

def aceptar_cookies(driver):
    cookies_button =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//button[@data-qa='accept-cookies']")))
    cookies_button.click()
    #time.sleep(2)
    header =  WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//header")))
    #scroll_shim(driver, header)
    cursor = ActionChains(driver)
    cursor.move_to_element(header).perform()
    #time.sleep(2)

def comprobar_estado_productos(driver,all_products):
    index = 0
    todos_los_productos = []
    for product in all_products:
        el_producto = {}
        indice = str(index)
        #Este IF filtra todos los items de publicidad que tiene Nike en la main page.
        if product.text != "Más información" and product.text != "":
            #Obtenemos data-qa: metadato de Nike para identificar cada producto.
            product_card_id = product.get_attribute("data-qa")
            print("----------------------Product number: {0}---------------------- \n {1}".format(indice,product.text))
            el_producto["Nombre"] = product.text.replace("\n","").strip()
            print("PRODUCT ID: ",product_card_id)
            #Por cada producto, aquellos que no son Más Información o vacío (lo cual es un anuncio en la página) -#if de arriba- localiza el producto de manera individual
            #ya que no era posible inspeccionar sus hijos (no se muy bien por qué)
            try:   
                estado_producto = driver.find_element_by_xpath("//div[@data-qa = '"+product_card_id+"']")
                #Movemos la pantalla y localizamos el cursor encima del elemento para desbloquear el boton, ergo el estado del producto
                scroll_shim(driver, estado_producto)
                #Creamos un cursor con el nuevo estado del explorador
                cursor = ActionChains(driver)
                time.sleep(1)
                cursor.move_to_element(estado_producto).perform()
                try:
                    #Inspeccionamos el elemento y obtenemos el boton
                    boton = estado_producto.find_element_by_xpath("//div[@data-qa = '"+product_card_id+"']//button")
                    #Hacemos una busqueda recurrente debido a que tarda en actualizarse el elemento
                    while boton.text == "":
                        boton = estado_producto.find_element_by_xpath("//div[@data-qa = '"+product_card_id+"']//button")
                    boton = boton.text
                    #Empezamos a crear los datos del producto en cuestión
                    el_producto["State"] = boton.strip()
                    el_producto["data-qa"] = product_card_id
                    #Los productos que se pueden comprar no tienen un botón como todos por debajo, sino un link a
                    #Es por eso que salta la excepción NoSuchElementException y en esta se prueba con el boton de comprar, que es
                    #//a[contains(@class,'btn')]
                except NoSuchElementException:
                    boton = estado_producto.find_element_by_xpath("//div[@data-qa = '"+product_card_id+"']//a[contains(@class,'btn')]")
                    while boton.get_attribute('innerHTML') == "":
                        boton = estado_producto.find_element_by_xpath("//div[@data-qa = '"+product_card_id+"']//a[contains(@class,'btn')]")
                    boton_innerHTML = boton.get_attribute('innerHTML')
                    if boton_innerHTML.strip() == "Comprar":
                        el_producto["State"] = boton_innerHTML.strip()
                        el_producto["data-qa"] = product_card_id
                        el_producto["url"] = boton.get_attribute('href')
                    pass 
            except NoSuchElementException: 
                pass
            todos_los_productos.append(el_producto)
            index += 1
    return todos_los_productos

def inspeccionar_main_page(driver,driver2): 
    all_products = buscar_todos_los_productos(driver)
    
    print("En total tenemos {0} productos en la pagina principal".format(len(all_products)))
    length = len(all_products)
    middle_index = length // 2
    #SPLIT IN CHUNKS. DIVIDE Y VENCERAS
    first_half = all_products[:middle_index]
    second_half = all_products[middle_index:]
    
    todos_los_productos = []

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        running_tasks = [executor.submit(comprobar_estado_productos, driver,first_half),executor.submit(comprobar_estado_productos, driver2,second_half)]
        for running_task in running_tasks:
            todos_los_productos += running_task.result()
    #print("Wat is todos",todos_los_productos)
    return todos_los_productos

def obtener_productos_disponibles(todos_los_productos):
    productos_disponibles = []
    #print("TODOS LOS PRODUCTOS:",todos_los_productos)
    for producto in todos_los_productos:
        if "State" in producto:
            if producto["State"] == "Comprar":
                productos_disponibles.append(producto)
    return productos_disponibles

def buscar_index_producto(todos_los_productos,identificador):
    for producto in todos_los_productos:
        if producto["data-qa"] == identificador:
            return todos_los_productos.index(producto)

#def obtener_precio_productos(driver,todos_los_productos):
    productos_disponibles = obtener_productos_disponibles(todos_los_productos)
    #print("Todos los productos disponibles: ",productos_disponibles)
    #DEPRECATED CODE, se queda por si algún día me hace falta.
    '''for item in productos_disponibles:       
        boton_comprar = driver.find_element_by_xpath("//div[@data-qa = '"+item+"']//a[contains(@class,'btn')]")
        #print("TIPO DE BOTON:",boton_comprar.get_attribute('href'))
        scroll_shim(driver, boton_comprar)
        #Creamos un cursor con el nuevo estado del explorador

        cursor = ActionChains(driver)
        time.sleep(1)
        cursor.move_to_element(boton_comprar).perform()
        boton_comprar.click()

        time.sleep(4)
        precio_zapatillas = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//div[@data-qa = 'price']")))
        print("PRECIO",precio_zapatillas.text)
        index = buscar_index_producto(todos_los_productos,item)
        todos_los_productos[index]["Precio"] = precio_zapatillas.text.strip()
        todas_las_tallas = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[contains(@class,'size-layout')]//li[@data-qa = 'size-available']")))
        lista_tallas = []
        for tallas in todas_las_tallas:
            lista_tallas.append(tallas.text.split(" ")[1])
        todos_los_productos[index]["Tallas"] = lista_tallas
        
        #captura_zapatilla = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//section[contains(@class,'card-product-component')]")))
        #//div[contains(@class,'pdp-container-inner')]
        
        capturar_producto(driver,todos_los_productos[index]["Nombre"])

        driver.back()
        load_more_botton = scroll_to_bottom(driver)
        load_more_botton.click()
        time.sleep(3)

    return todos_los_productos'''

def capturar_producto(driver,nombre_de_producto):
   
    driver.execute_script("document.body.style.MozTransform='scale(0.55)';")
    
    #body = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(@class,'headline')]")))
    ##CAMBIO DEBIDO A QUE LA PAGINA DE NIKE TIENE UN BUG CON UNA ZAPATILLA
    body = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//div[@data-qa = 'feed-menu']")))
    
    scroll_shim(driver, body)
    cursor = ActionChains(driver)
    cursor.move_to_element(body).perform()
    time.sleep(2)
    captura_zapatilla = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//section[contains(@class,'card-product-component')]")))
    prueba_top = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'feed-header')]")))

    div_zapatilla = captura_zapatilla.location
    sizeofdiv = captura_zapatilla.size
    dir_top_size =  prueba_top.size

    left = div_zapatilla['x']
    #top = dir_top['y'] - sizeofdiv['height']
    right = div_zapatilla['x'] + sizeofdiv['width']
    bottom = sizeofdiv['height']
    #print(left,top,right,bottom)

    driver.save_screenshot("mongodb/database/imagenes/"+nombre_de_producto+".png")
    print("-----Guardando la captura de {0}".format(nombre_de_producto))
    im = Image.open("mongodb/database/imagenes/"+nombre_de_producto+".png") # uses PIL library to open image in memory
    im = im.crop((left, 0 + (dir_top_size['height'])*3, right, bottom)) # defines crop points
    im.save("mongodb/database/imagenes/"+nombre_de_producto+".png") # saves new cropped image
    driver.execute_script("document.body.style.MozTransform='scale(1)';")

def generarjson(todos_los_productos,productos_disponibles):
    with open('mongodb/database/products/todos_los_productos.json','w') as jsonFile:
        json.dump(todos_los_productos, jsonFile)

    with open('mongodb/database/products/productos_disponibles.json','w') as jsonFile:
        json.dump(productos_disponibles, jsonFile)




def zapatillasdisponibles(update,context):
    """Lista las zapatillas de Nike disponibles."""
    #update.message.reply_text(nike.todos_los_productos)
    lista_productos_disponibles = ""
    for producto in nike.todos_los_productos:
        if producto["State"] == "Comprar":
            lista_productos_disponibles += "| "+producto["Nombre"]+" | Precio: "+producto["Precio"]+"| \n | Tallas: "
            for tallas_disponibles in producto["Tallas"]:
                lista_productos_disponibles += tallas_disponibles +"/"
            lista_productos_disponibles += tallas_disponibles +" |\n"
    update.message.reply_text(lista_productos_disponibles)

def zapatillasnodisponibles(update,context):
    """Lista las zapatillas de Nike no disponibles."""
    lista_productos_disponibles = ""
    for producto in nike.todos_los_productos:
        if producto["State"] != "Comprar":
            lista_productos_disponibles += "| "+producto["Nombre"]+" | Estado: "+producto["State"]+"| \n"
    update.message.reply_text(lista_productos_disponibles)

def send_pdf(update,context):
    """Envia el pdf generado a través del bot."""
    print("????aver",context.bot)
    print("2",context.bot_data)
    print(update)
    #print(update.bot)
    context.bot.send_document(chat_id=update.message.chat.id, document=open('primerpdf.pdf', 'rb'), filename="zapasguapasloco.pdf")
    #update.sendDocument(document=open('primerpdf.pdf', 'rb'))

def tallasdisponibles(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')
    print(update.message.text)
    tallas_buscadas = update.message.text.split(" ")[1:]
    print(tallas_buscadas)
    tallas_encontradas =[]

    for producto in productos_disponibles:
        if producto["Tallas"][0] == "Actualmente no quedan tallas":
            productos_disponibles.remove(producto)

    for producto in productos_disponibles:
        producto["talla-encontrada"] = ""
        for talla in producto["Tallas"]:
            for talla_buscada in tallas_buscadas:
                if talla_buscada == talla:
                    producto["talla-encontrada"] += talla_buscada +"/"
        tallas_encontradas.append(producto)
    print("Tallas encontradas: ",tallas_encontradas)  
    mensaje_respuesta = "Hemos encontrado estas zapatillas con la talla buscada!: \n"
    count = 0
    for zapatilla_con_talla in tallas_encontradas:
        if zapatilla_con_talla["talla-encontrada"] != "":
            count += 1
            mensaje_respuesta = "Talla/s :"+zapatilla_con_talla["talla-encontrada"] +"\n"+zapatilla_con_talla["Nombre"] +"\n"+zapatilla_con_talla["url"] + "\n"
            update.message.reply_text(mensaje_respuesta)
    print("En total {0} productos encontrados".format(count))
    if count == 0:
        update.message.reply_text("Actualmente no quedan zapatillas con la talla/s {0}".format(tallas_buscadas))   

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)
    print(update)
    print(context)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("2085627037:AAH9bMjh-amAABOz5FgKWu8kSQCu-PbiZBM", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("tallasdisponibles", tallasdisponibles))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("zapatillasdisponibles", zapatillasdisponibles))
    dp.add_handler(CommandHandler("zapatillasnodisponibles", zapatillasnodisponibles))
    dp.add_handler(CommandHandler("sendpdf", send_pdf))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def obtener_tallas_y_precio(driver,producto):
    precio_zapatillas = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, "//div[@data-qa = 'price']")))
    #print("PRECIO",precio_zapatillas.text)
    producto["Precio"] = precio_zapatillas.text.strip()
    try:
        todas_las_tallas = WebDriverWait(driver, 4).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[contains(@class,'size-layout')]//li[@data-qa = 'size-available']")))
        lista_tallas = []
        for tallas in todas_las_tallas:
            lista_tallas.append(tallas.text.split(" ")[1])  
        producto["Tallas"] = lista_tallas  
    except TimeoutException:
        lista_tallas = []
        print("Error obteniendo tallas para la zapatilla: "+producto["Nombre"].strip()+".Posiblemente agotada")
        lista_tallas.append("Actualmente no quedan tallas")
        producto["Tallas"] = lista_tallas
        raise
    
def concurrent_search(producto):  
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-default-apps')
    driver = webdriver.Firefox(options=options) # webdriver
    time.sleep(2)
    driver.get(producto["url"])  
    aceptar_cookies(driver)
    try:
        obtener_tallas_y_precio(driver,producto)
    except:
        pass
    capturar_producto(driver,producto["Nombre"].strip())
    
    driver.quit()
  

if "__main__" == __name__:
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    nike = NikeShop()
    
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(nike.todos_los_productos)
    print("---------------------------------------------------------------------------------------------------------------------------")
    
    productos_disponibles = obtener_productos_disponibles(nike.todos_los_productos)

    with futures.ThreadPoolExecutor() as executor: #default/optimized number of threads
        executor.map(concurrent_search, productos_disponibles)
    
    print("\n----------------------------------------------------------------------------------PRODUCTOS DISPONIBLES:----------------------------------------------------------------------------------\n",productos_disponibles)
    pdf = PDF(productos_disponibles)

    generarjson(nike.todos_los_productos,productos_disponibles)
    #nike.driver.quit()
    
    main()