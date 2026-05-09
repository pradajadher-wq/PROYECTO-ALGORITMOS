lado1=float(input("Digite un lado del triangulo: "))
lado2=float(input("Digite otro del triangulo: "))
lado3=float(input("Digite otro lado del triangulo: "))

if (lado1+lado2>lado3 and lado2+lado3>lado1 and lado1+lado3>lado2):
    if (lado1==lado2==lado3):
        print("Triangulo equilatero")
    elif (lado1==lado2 or lado2==lado3 or lado3==lado1):
        print("Triangulo isosceles")
    else:
        print("Triangulo escaleno")
else:
    print("Los lados no corresponde a un triangulo")