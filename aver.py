lista_tallas = {"Popular Size": {9.0: 359.0, 9.5: 374.3333333333333, 10.0: 386.15384615384613, 10.5: 396.44444444444446, 11.0: 436.1111111111111, 11.5: 0, 12.0: 558.0}}
string_final = ""
'''for talla,precio in lista_tallas:
    string_final += "Talla: {0} \n Precio medio de venta: {1}".format(talla,precio)'''
print(lista_tallas)
for hola in lista_tallas["Popular Size"]:
    print(hola)
    print(lista_tallas["Popular Size"][hola])