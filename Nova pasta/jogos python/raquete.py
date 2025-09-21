import pygame
import random

# Inicializa o Pygame
pygame.init()

# Definindo as cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (0, 0, 255)

# Tamanho da tela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Jogo de Raquete 2D')

# Raquete
raquete_LARGURA = 15
raquete_ALTURA = 100
raquete_VELOCIDADE = 10

# Bola
bola_RAIO = 10
bola_VELOCIDADE = 5

# Função para desenhar a raquete
def desenhar_raquete(x, y):
    pygame.draw.rect(tela, AZUL, (x, y, raquete_LARGURA, raquete_ALTURA))

# Função para desenhar a bola
def desenhar_bola(x, y):
    pygame.draw.circle(tela, BRANCO, (x, y), bola_RAIO)

# Função principal
def jogo():
    # Posições iniciais das raquetes e bola
    raquete_esquerda_y = (ALTURA - raquete_ALTURA) // 2
    raquete_direita_y = (ALTURA - raquete_ALTURA) // 2
    bola_x = LARGURA // 2
    bola_y = ALTURA // 2

    bola_dx = random.choice([bola_VELOCIDADE, -bola_VELOCIDADE])  # Direção horizontal
    bola_dy = random.choice([bola_VELOCIDADE, -bola_VELOCIDADE])  # Direção vertical

    # Pontuação
    pontos_esquerda = 0
    pontos_direita = 0

    # Controle do jogo
    clock = pygame.time.Clock()
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        # Controle das raquetes
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_w] and raquete_esquerda_y > 0:
            raquete_esquerda_y -= raquete_VELOCIDADE
        if teclas[pygame.K_s] and raquete_esquerda_y < ALTURA - raquete_ALTURA:
            raquete_esquerda_y += raquete_VELOCIDADE
        if teclas[pygame.K_UP] and raquete_direita_y > 0:
            raquete_direita_y -= raquete_VELOCIDADE
        if teclas[pygame.K_DOWN] and raquete_direita_y < ALTURA - raquete_ALTURA:
            raquete_direita_y += raquete_VELOCIDADE

        # Movimento da bola
        bola_x += bola_dx
        bola_y += bola_dy

        # Colisão da bola com a parte superior e inferior da tela
        if bola_y - bola_RAIO <= 0 or bola_y + bola_RAIO >= ALTURA:
            bola_dy = -bola_dy  # Inverte a direção vertical

        # Colisão da bola com as raquetes
        if bola_x - bola_RAIO <= raquete_LARGURA and raquete_esquerda_y < bola_y < raquete_esquerda_y + raquete_ALTURA:
            bola_dx = -bola_dx
        if bola_x + bola_RAIO >= LARGURA - raquete_LARGURA and raquete_direita_y < bola_y < raquete_direita_y + raquete_ALTURA:
            bola_dx = -bola_dx

        # Se a bola passar pela raquete (gol)
        if bola_x - bola_RAIO <= 0:
            pontos_direita += 1
            bola_x = LARGURA // 2
            bola_y = ALTURA // 2
            bola_dx = random.choice([bola_VELOCIDADE, -bola_VELOCIDADE])
            bola_dy = random.choice([bola_VELOCIDADE, -bola_VELOCIDADE])

        if bola_x + bola_RAIO >= LARGURA:
            pontos_esquerda += 1
            bola_x = LARGURA // 2
            bola_y = ALTURA // 2
            bola_dx = random.choice([bola_VELOCIDADE, -bola_VELOCIDADE])
            bola_dy = random.choice([bola_VELOCIDADE, -bola_VELOCIDADE])

        # Preencher o fundo da tela
        tela.fill(PRETO)

        # Desenhar os objetos na tela
        desenhar_raquete(30, raquete_esquerda_y)
        desenhar_raquete(LARGURA - 30 - raquete_LARGURA, raquete_direita_y)
        desenhar_bola(bola_x, bola_y)

        # Mostrar a pontuação
        fonte = pygame.font.Font(None, 36)
        texto = fonte.render(f"{pontos_esquerda} - {pontos_direita}", True, BRANCO)
        tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 20))

        # Atualizar a tela
        pygame.display.flip()

        # Controlar a taxa de quadros
        clock.tick(60)

    pygame.quit()

# Iniciar o jogo
jogo()
