import random

segredo = random.randint(1, 20)
tentativas = 0

print("🎯 Tente adivinhar o número (1 a 20)")

while True:
    chute = int(input("Seu palpite: "))
    tentativas += 1

    if chute == segredo:
        print(f"Parabéns! Você acertou em {tentativas} tentativas 🎉")
        break
    elif chute < segredo:
        print("Muito baixo ⬇️")
    else:
        print("Muito alto ⬆️")
