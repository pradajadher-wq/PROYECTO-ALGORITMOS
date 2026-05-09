n=int(input("¿Cuantos numeros desea ingresar? "))
mayores=0
menores=0
ceros=0
for i in range (n):
    num=int(input("Ingrese los numeros: "))
    
    if num>0:
        mayores +=1
    elif num<0:
        menores+=1
    else:
        ceros +=1
print("Mayores que 0:    ", mayores)
print("Menores que 0: ", menores)
print("Iguales a cero: ", ceros)

    
    