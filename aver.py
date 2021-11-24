lista_tallas = {9.0: {'Media recaudada': 359.0, 'Max sale': 399.0, 'Total ventas': 17.0}, 9.5: {'Media recaudada': 374.3333333333333, 'Max sale': 392.0, 'Total ventas': 6.0}, 10.0: {'Media recaudada': 386.15384615384613, 'Max sale': 434.0, 'Total ventas': 13.0}, 10.5: {'Media recaudada': 396.44444444444446, 'Max sale': 533.0, 'Total ventas': 18.0}, 11.0: {'Media recaudada': 436.1111111111111, 'Max sale': 491.0, 'Total ventas': 9.0}, 11.5: 0, 12.0: {'Media recaudada': 558.0, 'Max sale': 576.0, 'Total ventas': 2.0}}
string_final = ""
for talla,datos in lista_tallas.items():
    print(datos)
    print(talla)
    print(type(datos))
    if datos:
        string_final += "Talla: {0} | Precio medio de venta: {1} | Precio maximo de venta: {2} | Total de ventas: {3}\n".format(talla,str(datos["Media recaudada"]),str(datos["Max sale"]),str(datos["Total ventas"]))
