opcion=0
cont_A=0
cont_B=0
cont_C=0
cont_D=0
totalcandidatas=0
sumacandidatas=0
cent=""
while opcion != 4:
    print("     MENU DE OPCIONES     ")
    print("\n1. Ingresar puntajes del jurado")
    print("\n2. Mostrar puntaje promedio del grupo de candidatas")
    print("\n3. Cantidad de candidatas procesadas por categoria")
    print("\n4. Terminar")
    opcion=int(input("Escoja una opcion 1-4: "))
    match opcion:
        case 1:
            cent=""
            while cent != " ":
                print("\nIngrese candidata", totalcandidatas+1)
                p1=int(input("Ingrese el primer puntaje (0-10): "))
                while p1<0 or p1>10:
                    p1=int(input("Ingrese un puntaje valido: "))
                p2=int(input("Ingrese el segundo puntaje (0-10): "))
                while p2<0 or p2>10:
                    p2=int(input("Ingrese un puntaje valido: "))
                p3=int(input("Ingrese el tercer puntaje (0-10): "))
                while p3<0 or p3>10:
                    p3=int(input("Ingrese un puntaje valido: "))
                cent=str(input("Si desea ingresar otro estudiante(enter), para salir espacio: "))
                puntajefinal=p1*0.50+p2*0.25+p3*0.30
                sumacandidatas +=puntajefinal
                totalcandidatas +=1
                if puntajefinal >= 8.0:
                    cont_A +=1
                elif puntajefinal >= 6.0:
                    cont_B +=1
                elif puntajefinal >= 4.0:
                    cont_C +=1
                else:
                    cont_D +=1    
        case 2: 
            if totalcandidatas>0:
                promedio=sumacandidatas/totalcandidatas
                print("El puntaje promedio de las candidatas es: ", promedio)
            else:
                print("Ingrese los puntajes de las candidatas: ")
        case 3:
            if totalcandidatas>0:
                print("Cantidad de candidatas en la categoria A: ", cont_A)
                print("Cantidad de candidatas en la categoria B: ", cont_B)
                print("Cantidad de candidatas en la categoria C: ", cont_C)
                print("Cantidad de candidatas en la categoria D: ", cont_D)
            else:
                print("Ingrese los puntajes de las candidatas")
            
            
            
            
        
            
        