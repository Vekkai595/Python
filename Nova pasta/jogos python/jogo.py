import random

print("🎲 Bem-vindo ao jogo de Adivinhação!")
print("Estou pensando em um número entre 1 e 100...")

# Gera um número aleatório entre 1 e 100
numero_secreto = random.randint(1, 100)
tentativas = 0

while True:
    tentativa = input("Digite seu palpite: ")
    
    # Validação básica
    if not tentativa.isdigit():
        print("Digite apenas números!")
        continue

    tentativa = int(tentativa)
    tentativas += 1

    if tentativa < numero_secreto:
        print("🔻 Muito baixo! Tente novamente.")
    elif tentativa > numero_secreto:
        print("🔺 Muito alto! Tente novamente.")
    else:
        print(f"🎉 Parabéns! Você acertou em {tentativas} tentativa(s)!")
        break
