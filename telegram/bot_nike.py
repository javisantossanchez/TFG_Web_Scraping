from math import prod
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import pymongo
import logging
import time

def obtain_availables_shoes_from_mongo(myclient):
    mydb = myclient["nike"]
    mycol = mydb["zapas_nike"]

    query_zapatillas_disponibles = { "State": "Comprar" }

    zapatillasdisponibles = mycol.find(query_zapatillas_disponibles,{"_id":0,"Nombre":1,"Precio":2,"Tallas":3,"url":4})
    zapatillasdisponibles = list(zapatillasdisponibles)
    zapatillasdisponibles = [x for x in zapatillasdisponibles if "Colección" not in x["Nombre"]]
    lista_nombres_disponibles = [x["Nombre"] for x in zapatillasdisponibles if "Colección" not in x["Nombre"]]

    return zapatillasdisponibles
    
def zapatillasdisponibles(update,context):
    """Lista las zapatillas de Nike disponibles."""

    #Definimos la conexión con la BD.
    myclient = pymongo.MongoClient(
            'mongodb://mongo:27017/',
            username='root',
            password='example')
    #Llamamos a la BD
    zapatillas_disponibles = obtain_availables_shoes_from_mongo(myclient)
    lista_productos_disponibles = ""
    #Creamos el String que respondera al usuario
    for producto in zapatillas_disponibles:
        lista_productos_disponibles += "| "+producto["Nombre"]+" | Precio: "+producto["Precio"]+"| \n | Tallas: "
        for tallas_disponibles in producto["Tallas"]:
            lista_productos_disponibles += tallas_disponibles +"/"
        lista_productos_disponibles += tallas_disponibles +" |\n"
    update.message.reply_text(lista_productos_disponibles)

def zapatillasnodisponibles(update,context):
    """Lista las zapatillas de Nike no disponibles."""
    #Definimos la conexion a la BD
    myclient = pymongo.MongoClient(
            'mongodb://mongo:27017/',
            username='root',
            password='example')
    mydb = myclient["nike"]
    mycol = mydb["zapas_nike"]
    #Pedimos todas aquellas zapatillas que no estan disponibles
    #Esperamos obtener el Nombre, Precio y State, que son las columnas de la BD
    zapatillasnodisponibles = mycol.find({"State": {"$ne" : "Comprar"}},{"_id":0,"Nombre":1,"Precio":2,"State":3})

    lista_productos_disponibles = ""
    for producto in zapatillasnodisponibles:
        lista_productos_disponibles += "| "+producto["Nombre"]+" | Estado: "+producto["State"]+"| \n"
    update.message.reply_text(lista_productos_disponibles)

def send_pdf(update,context):
    """Envia el pdf generado a través del bot."""
    context.bot.send_document(chat_id=update.message.chat.id, document=open('primerpdf.pdf', 'rb'), filename="NikeScraperLastSearch.pdf")

def tallasdisponibles(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hola!')

    tallas_buscadas = update.message.text.split(" ")[1:]
    tallas_encontradas =[]
    myclient = pymongo.MongoClient(
            'mongodb://mongo:27017/',
            username='root',
            password='example')

    zapatillas_disponibles = obtain_availables_shoes_from_mongo(myclient)
    for producto in zapatillas_disponibles:
        if producto["Tallas"][0] == "Actualmente no quedan tallas":
            zapatillas_disponibles.remove(producto)
    for producto in zapatillas_disponibles:
        producto["talla-encontrada"] = ""
        for talla in producto["Tallas"]:
            for talla_buscada in tallas_buscadas:
                if talla_buscada == talla:
                    producto["talla-encontrada"] += talla_buscada +"/"
        tallas_encontradas.append(producto)
    mensaje_respuesta = "Hemos encontrado estas zapatillas con la/s talla/s buscada!: \n"
    update.message.reply_text(mensaje_respuesta)
    count = 0
    for zapatilla_con_talla in tallas_encontradas:
        if zapatilla_con_talla["talla-encontrada"] != "":
            count += 1
            mensaje_respuesta = "Talla/s :"+zapatilla_con_talla["talla-encontrada"] +"\n"+zapatilla_con_talla["Nombre"] +"\n"+zapatilla_con_talla["url"] + "\n"
            update.message.reply_text(mensaje_respuesta)
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




if "__main__" == __name__:  
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)
    main()


