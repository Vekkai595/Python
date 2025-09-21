import random
import json
import os
from datetime import datetime
from colorama import Fore, Style, init

# inicializa colorama
init(autoreset=True)

# ===============================
# 🔹 Dados base
# ===============================
BIOMAS = ["Floresta", "Deserto", "Montanhas", "Pântano", "Campos", "Costa", "Ilha"]
CLASSES = ["Guerreiro", "Mago", "Arqueiro", "Ladino", "Clérigo", "Bárbaro", "Feiticeiro"]
TRAÇOS = ["corajoso", "ganancioso", "sábio", "impulsivo", "astuto", "leal", "sombrio"]
MOTIVOS = ["vingança", "riqueza", "paz", "conhecimento", "glória", "redenção"]
FACÇÕES = ["Ordem da Luz", "Clã das Sombras", "Guilda dos Mercadores", "Império de Ferro", "Povo Livre"]
ALINHAMENTOS = ["Bom", "Neutro", "Maligno"]
MISSÕES = [
    "recuperar um artefato perdido",
    "derrotar uma criatura lendária",
    "proteger uma vila sob ataque",
    "escoltar uma caravana perigosa",
    "explorar ruínas esquecidas",
    "negociar paz entre facções rivais"
]
RECOMPENSAS = ["ouro", "magia antiga", "armas raras", "conhecimento proibido", "alianças poderosas"]

# ===============================
# 🔹 Funções
# ===============================
def gerar_personagem():
    nome = random.choice(["Arin", "Kael", "Lyra", "Mira", "Thorn", "Darian", "Eryn", "Zarek"])
    classe = random.choice(CLASSES)
    traço = random.choice(TRAÇOS)
    motivo = random.choice(MOTIVOS)
    return {
        "nome": nome,
        "classe": classe,
        "traço": traço,
        "motivo": motivo
    }

def gerar_faccao():
    return {
        "nome": random.choice(FACÇÕES),
        "alinhamento": random.choice(ALINHAMENTOS),
        "influência": random.randint(1, 100)
    }

def gerar_missao():
    return {
        "objetivo": random.choice(MISSÕES),
        "dificuldade": random.choice(["Fácil", "Média", "Difícil", "Épica"]),
        "recompensa": random.choice(RECOMPENSAS)
    }

def gerar_mapa(tamanho=5):
    return [[random.choice(BIOMAS) for _ in range(tamanho)] for _ in range(tamanho)]

def rolagem_d20():
    return random.randint(1, 20)

def salvar_mundo(mundo, arquivo="mundo.json"):
    with open(arquivo, "w") as f:
        json.dump(mundo, f, indent=2, ensure_ascii=False)

# ===============================
# 🔹 Programa principal
# ===============================
def main():
    print(Fore.GREEN + "🌍 Gerador Automático de Mundos de RPG")
    print(Fore.YELLOW + "Cria mapas, personagens, facções e missões de forma procedural.\n")

    mundo = {
        "criado_em": str(datetime.now()),
        "mapa": gerar_mapa(),
        "personagens": [gerar_personagem() for _ in range(3)],
        "facções": [gerar_faccao() for _ in range(2)],
        "missões": [gerar_missao() for _ in range(3)]
    }

    # mostra mapa
    print(Fore.CYAN + "\n🗺️  Mapa do Mundo:")
    for linha in mundo["mapa"]:
        print(" | ".join(linha))

    # mostra personagens
    print(Fore.MAGENTA + "\n👤 Personagens:")
    for p in mundo["personagens"]:
        print(f"- {p['nome']} ({p['classe']}, {p['traço']}, busca {p['motivo']})")

    # mostra facções
    print(Fore.BLUE + "\n🏰 Facções:")
    for f in mundo["facções"]:
        print(f"- {f['nome']} ({f['alinhamento']}, influência {f['influência']})")

    # mostra missões
    print(Fore.YELLOW + "\n📖 Missões:")
    for m in mundo["missões"]:
        print(f"- {m['objetivo']} (dificuldade: {m['dificuldade']}, recompensa: {m['recompensa']})")

    # rolagem d20
    print(Fore.RED + "\n🎲 Rolagem de dado d20 para evento inesperado...")
    time.sleep(1)
    dado = rolagem_d20()
    print(Fore.RED + f"Resultado: {dado}")
    if dado == 20:
        print(Fore.GREEN + "✨ Um evento épico acontece! O mundo muda drasticamente.")
    elif dado == 1:
        print(Fore.RED + "💀 Catástrofe! Algo terrível ocorre no mundo.")
    else:
        print(Fore.YELLOW + "Nada fora do comum acontece.")

    # salvar mundo
    salvar_mundo(mundo)
    print(Fore.GREEN + "\n✅ Mundo salvo em 'mundo.json'.")

# ===============================
if __name__ == "__main__":
    import time
    main()
