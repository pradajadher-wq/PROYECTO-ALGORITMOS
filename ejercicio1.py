contador=0
suma=0
l1=int(input("Ingrese el limite inferior del intervalo: "))
l2=int(input("Ingrese el limite superior del intervalo: "))
while l1>l2: 
    print("Vuelva a escribir limites validos: ")
    l1=int(input("Ingrese el limite inferior del intervalo: "))
    l2=int(input("Ingrese el limite superior del intervalo: "))
else:
    n=int(input("Introduzca numeros (0 para salir)"))
    while n != 0:
        n=int(input("Introduzca numeros (0 para salir)"))
        if n>l1 and n<l2:
            suma += n
        elif n<l1 or n>l2:
            contador +=1
        elif n==l1 or n==l2:
            print("Ha introducido numero igual al intervalo")
print ("La suma de los numeros dentro del intervalo es ",suma)
print("Los numeros por fuera del intervalo son: ", contador)