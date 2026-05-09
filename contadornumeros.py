#CALCULO DE ESTADISTICAS PARA UN GRUPO DE ESTUDIANTES
suma=0
contador=0
num=float(input("Ingrese numeros (0 para terminar): "))
while num != 0:
    suma +=num
    contador +=1
    num=float(input("Ingrese numeros (0 para terminar): "))
if contador > 0:
    media = suma / contador
    print("Suma:", suma)
    print("Media:", media)
else:
    print("No se ingresaron números")
print("La suma de los numeros ingresados es", suma)
print("La media de los numeros ingresados es", media)
