n1=int(input("Ingrese el primer numero: "))
n2=int(input("Ingrese el sengundo numero: "))
for i in range (n1,n2,1):
    if i%2==0:
        print("     Menu de opciones    ")
        print("\n1. Ingresa calificaciones de los modelos")
        print("\n2. Numero total de los modelos analizados")
        print("\n3. NUmero de modelos clasificados en cada nivel")
        print("\n4. Mayor y menor precision encontrada")
        print("\n5. Mensaje globlal sobre el rendimiento promedio del conjunto de modelos")
        print("\n6. Terminar")
        opcion=int(input("Escoja una opcion 1-6"))
        