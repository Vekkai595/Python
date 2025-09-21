import pygame
import random
import sys
import time

# Inicializar
pygame.init()

# Tela
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Fuja do Bixinho 🏃‍♂️")

# Cores
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)

# Jogador
jogador = pygame.Rect(400, 300, 40, 40)
vel_jogador = 5

# Fase
fase = 1
tempo_fase = [10, 20, 30, 40, 50]  # tempo pra cada fase
inicio_fase = time.time()

# Bichinhos
def gerar_bixinhos(n):
    return [pygame.Rect(random.randint(0, LARGURA-30), random.randint(0, ALTURA-30), 30, 30) for _ in range(n)]

bixinhos = gerar_bixinhos(fase)

def mover_bixinhos(bixinhos, jogador):
    for bixo in bixinhos:
        if bixo.x < jogador.x:
            bixo.x += 2
        elif bixo.x > jogador.x:
            bixo.x -= 2
        if bixo.y < jogador.y:
            bixo.y += 2
        elif bixo.y > jogador.y:
            bixo.y -= 2

def mostrar_texto(texto, tamanho, y):
    fonte = pygame.font.SysFont(None, tamanho)
    render = fonte.render(texto, True, (0, 0, 0))
    tela.blit(render, (20, y))

# Loop do jogo
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    tela.fill(BRANCO)

    # Tempo
    tempo_passado = int(time.time() - inicio_fase)
    mostrar_texto(f"Fase {fase} - Tempo: {tempo_passado}/{tempo_fase[min(fase-1, len(tempo_fase)-1)]}", 36, 10)

    # Controles
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jogador.left > 0:
        jogador.x -= vel_jogador
    if teclas[pygame.K_RIGHT] and jogador.right < LARGURA:
        jogador.x += vel_jogador
    if teclas[pygame.K_UP] and jogador.top > 0:
        jogador.y -= vel_jogador
    if teclas[pygame.K_DOWN] and jogador.bottom < ALTURA:
        jogador.y += vel_jogador

    # Mover bichinhos
    mover_bixinhos(bixinhos, jogador)

    # Desenhar jogador e bichos
    pygame.draw.rect(tela, AZUL, jogador)
    for bixo in bixinhos:
        pygame.draw.rect(tela, VERMELHO, bixo)

        # Colisão = Game over
        if jogador.colliderect(bixo):
            mostrar_texto("GAME OVER!", 72, 250)
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.quit()
            sys.exit()

    # Próxima fase
    if tempo_passado >= tempo_fase[min(fase-1, len(tempo_fase)-1)]:
        fase += 1
        bixinhos = gerar_bixinhos(fase)
        inicio_fase = time.time()

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
