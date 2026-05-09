opcion=0
cont_A=0
cont_B=0
cont_C=0
cont_D=0
cent=" "
totalnotas=0
totalestudiantes=0
while opcion !=4:
    print("MENU DE OPCIONES")
    print("\n1. Ingresar notas")
    print("\n2. Mostrar nota promedio del grupo")
    print("\n3. Cantidad de estudiantes procesador por categoria")
    print("\n4. Terminar")
    opcion=int(input(" Escoja una opcion 1-4: "))
    match opcion:
        case 1:
            cent= " "
            while cent != "s":
                n1=float(input("Nota 1: "))
                while n1<0 or n1>5:
                    n1=float(input("Error vuelva a ingresar una nota valida: "))
                n2=float(input("Nota 2: "))
                while n2<0 or n2>5:
                    n2=float(input("Error vuelva a ingresar una nota valida: "))
                n3=float(input("Nota 3: "))
                while n3<0 or n3>5:
                    n3=float(input("Error vuelva a ingresar una nota valida: "))
                notafinal=n1*0.40 + n2*0.30 + n3*0.30
                totalnotas += notafinal
                totalestudiantes +=1
                if notafinal >=4.0:
                    cont_A +=1
                elif notafinal >=3.0:
                    cont_B +=1
                elif notafinal >=2.0:
                    cont_C +=1
                else:
                    cont_D +=1
                cent=str(input("Si desea ingresa otro estudiante enter (Para terminar s )\n"))
        case 2:
            if totalestudiantes>0:
                promedio= totalnotas/totalestudiantes
                print("La nota promedio del grupo es: ", promedio)
            else:
                print("No hay datos ingrese estudiantes")
        case 3:
            if totalestudiantes>0:
                print("Catidad de estudiantes categoria A: ", cont_A)
                print("Catidad de estudiantes categoria B: ", cont_B)
                print("Catidad de estudiantes categoria C: ", cont_C)
                print("Catidad de estudiantes categoria D: ", cont_D)
            else:
                print("No hay datos ingrese estudiantes")
            
        