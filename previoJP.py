LIMITE_EXCELENTE=90
LIMITE_BUENO=75
LIMITE_ACEPTABLE=60
centinela =""
opcion=0
numdemodelos=0
cont_E=0
cont_B=0
cont_A=0
cont_D=0
mayoromenor=0
suma=0
while opcion != 6:
    print("     MENU DE OPCIONES    ")
    print("\n1. Ingresa calificaciones de los modelos: ")
    print("\n2. Numero total de los modelos analizados")
    print("\n3. Numero de modelos clasificados en cada nivel")
    print("\n4. Mayor y menor precision encontrada")
    print("\n5. Mensaje globlal sobre el rendimiento promedio del conjunto de modelos")
    print("\n6. Terminar")
    opcion=int(input("Escoja una opcion 1-6: "))
    match opcion:
        case 1:
            centinela = ""
            while centinela != "-1":
                accuracy=float(input("Ingrese la precision del modelo: "))
                while accuracy>100 or accuracy<0:
                    accuracy=float(input("Ingrese una precision valida del modelo: "))
                centinela=str(input("Si desea agregar otra presicion (enter), para salir introduzca (-1): "))
                numdemodelos +=1
                suma+=accuracy
                if accuracy >=90:
                    cont_E +=1
                elif accuracy >= LIMITE_BUENO and accuracy<LIMITE_EXCELENTE:
                    cont_B +=1
                elif accuracy >= LIMITE_ACEPTABLE and accuracy<LIMITE_BUENO:
                    cont_A +=1
                else:
                    cont_D +=1
                if mayoromenor == 0:
                    mayor=accuracy
                    menor=accuracy
                else:
                    if accuracy>mayor:
                        mayor=accuracy
                    if accuracy<menor:
                        menor=accuracy
                mayoromenor +=1     
        case 2:
            if numdemodelos>0:
                print("El total de modelos analizados es: ",numdemodelos)
            else:
                print("Ingrese las presiciones de los modelos")
        case 3:
            if numdemodelos>0:
                print("Excelente: ",cont_E)
                print("Bueno: ",cont_B)
                print("Aceptable: ", cont_A)
                print("Deficiente: ",cont_D)
            else:
                print("Ingrese las presiciones de los modelos")
        case 4:
            if mayoromenor>0:
                print("Mayor: ",mayor)
                print("Menor: ",menor)
            else:
                print("Ingrese las presiciones de los modelos")
        case 5:
            if numdemodelos>0:
                promedio=suma/numdemodelos
                if promedio >= 90:
                    print("Rendimiento global excelente")
                elif promedio >=75 and promedio<90:
                    print("Rendiminto global bueno")
                elif promedio>=60 and promedio<75:
                    print("Rendimiento global aceptable")
                else:
                    print("Rendimiento global deficiente")
            else:
                print("Ingrese las presiciones de los modelos")

                
        
                
            
        