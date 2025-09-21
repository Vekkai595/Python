texto = input("Escreva algo para salvar no arquivo: ")

with open("bloco.txt", "a") as f:
    f.write(texto + "\n")

print("Texto salvo em bloco.txt ✅")
