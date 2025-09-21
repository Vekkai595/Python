a = float(input("Primeiro número: "))
b = float(input("Segundo número: "))
op = input("Operação (+ - * /): ")

if op == "+":
    print("Resultado:", a + b)
elif op == "-":
    print("Resultado:", a - b)
elif op == "*":
    print("Resultado:", a * b)
elif op == "/":
    print("Resultado:", a / b)
else:
    print("Operação inválida!")
