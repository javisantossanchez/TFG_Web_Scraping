import pymongo


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