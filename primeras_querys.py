import pymongo

#myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myclient = pymongo.MongoClient('mongodb://localhost:27017/',
                  username='root',
                 password='example')
mydb = myclient["nike"]
mycol = mydb["zapas_nike"]

myquery = { "State": "Comprar" }

mydoc = mycol.find(myquery)

for x in (mydoc):
  print(x)