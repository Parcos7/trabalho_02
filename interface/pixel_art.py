import pygame

# =============================================================================
# FUNÇÃO AUXILIAR DE RENDERIZAÇÃO
# =============================================================================
def desenhar_sprite(tela, matriz_linhas, paleta_cores, pos_x, pos_y, tam_px=2):
    for lin_idx, linha in enumerate(matriz_linhas):
        for col_idx, char in enumerate(linha):
            if char in paleta_cores and char not in (' ', '.'):
                cor = paleta_cores[char]
                pygame.draw.rect(
                    tela,
                    cor,
                    (pos_x + col_idx * tam_px, pos_y + lin_idx * tam_px, tam_px, tam_px)
                )


# =============================================================================
# SPRITES DO SISTEMA OPERACIONAL (CYBERPIXEL OS)
# =============================================================================

# 1. Ícone da Lixeira (Vazia)
SPRITE_LIXEIRA = [
    "  ......BBBBBBBB......  ",
    "  .....BBBBBBBBBB.....  ",
    "  ....BBBBBBBBBBBB....  ",
    "  ..WWWWWWWWWWWWWWWW..  ",
    "  ..W..............W..  ",
    "  ..W.CC.CC.CC.CC..W..  ",
    "  ..W.CC.CC.CC.CC..W..  ",
    "  ...W.CC.CC.CC.CC.W..  ",
    "  ...W.CC.CC.CC.CC.W..  ",
    "  ...W.CC.CC.CC.CC.W..  ",
    "  ....W.CC.CC.CC.CCW..  ",
    "  ....W.CC.CC.CC.CCW..  ",
    "  ....WWWWWWWWWWWWWW..  ",
    "  .....BBBBBBBBBBBB...  "
]
PALETA_LIXEIRA = {
    "B": (50, 70, 100),
    "W": (180, 200, 220),
    "C": (100, 140, 180)
}

# 2. Ícone do Navegador (Paródia: "Cyber Explorer" / Laboratório Isolado)
SPRITE_NAVEGADOR = [
    "  ......EEEEEEEE......  ",
    "  ....EEEEEEEEEEEE....  ",
    "  ...EEE........EEE...  ",
    "  ..EEE...BBBB...EEE..  ",
    "  ..EE...BBBBBB...EE..  ",
    "  .EEE..BBBBBBBB...E..  ",
    "  .EEEEEEEEEEEEEEEE...  ",
    "  .EEEEEEEEEEEEEE.....  ",
    "  .EEE..BBBBBBBB......  ",
    "  ..EE...BBBBBB.......  ",
    "  ..EEE...BBBB........  ",
    "  ...EEE........EEE...  ",
    "  ....EEEEEEEEEEEE....  ",
    "  ......EEEEEEEE......  "
]
PALETA_NAVEGADOR = {
    "E": (30, 144, 255),   # Azul clássico
    "B": (255, 215, 0)     # Dourado brilhante / anel
}

# 3. Ícone do Explorador de Arquivos (Pasta Amarela Clássica)
SPRITE_PASTA = [
    "  ..FFFF..............  ",
    "  .FFFFFF.............  ",
    "  .FFFFFFFFFFFFFFFF...  ",
    "  .FYYYYYYYYYYYYYYF...  ",
    "  .FYYYYYYYYYYYYYYF...  ",
    "  .FYYYYYYYYYYYYYYYYF.  ",
    "  .FYYYYYYYYYYYYYYYYF.  ",
    "  .FYYYYYYYYYYYYYYYYF.  ",
    "  .FYYYYYYYYYYYYYYYYF.  ",
    "  .FYYYYYYYYYYYYYYYYF.  ",
    "  .FYYYYYYYYYYYYYYYYF.  ",
    "  .FYYYYYYYYYYYYYYYYF.  ",
    "  .FFFFFFFFFFFFFFFFFF.  "
]
PALETA_PASTA = {
    "F": (180, 130, 20),   # Borda da pasta
    "Y": (255, 205, 70)    # Amarelo pasta
}

# 4. Logotipo CyberPixel OS (Emblema Retro Tecnológico)
SPRITE_LOGO_OS = [
    "  ....CCCCCCCC....  ",
    "  ..CCCCCCCCCCCC..  ",
    "  .CCCC.GGGG.CCCC.  ",
    "  .CCC.GGGGGG.CCC.  ",
    "  .CCC.GGGGGG.CCC.  ",
    "  .CCCC.GGGG.CCCC.  ",
    "  ..CCCCCCCCCCCC..  ",
    "  ....CCCCCCCC....  "
]
PALETA_LOGO_OS = {
    "C": (0, 180, 255),    # Ciano
    "G": (0, 255, 120)     # Verde neon
}

# 5. Ícone do Botão Iniciar
SPRITE_BOTAO_INICIAR = [
    "  .GGGGGGGGGGGGGGGG.  ",
    "  .GGGGGGGGGGGGGGGG.  ",
    "  .GG..WW..WW..WWGG.  ",
    "  .GG..WW..WW..WWGG.  ",
    "  .GGGGGGGGGGGGGGGG.  ",
    "  .GG..WW..WW..WWGG.  ",
    "  .GG..WW..WW..WWGG.  ",
    "  .GGGGGGGGGGGGGGGG.  "
]
PALETA_BOTAO_INICIAR = {
    "G": (46, 139, 87),    # Verde Iniciar
    "W": (240, 255, 240)   # Branco
}

# 6. Avatar / Ícone de Usuário (Admin SOC vs Convidado)
SPRITE_USER_ADMIN = [
    "  .....BBBBBBB.....  ",
    "  ....BBBBBBBBB....  ",
    "  ....BBBBBBBBB....  ",
    "  .....BBBBBBB.....  ",
    "  ......CCCCC......  ",
    "  ....CCCCCCCCC....  ",
    "  ...CCCCCCCCCCC...  ",
    "  ..CCCCCCCCCCCCC..  ",
    "  ..CCCCCCCCCCCCC..  "
]
PALETA_USER_ADMIN = {
    "B": (0, 220, 255),    # Capacete/Cabelo ciano SOC
    "C": (20, 60, 110)     # Uniforme azul escuro
}

SPRITE_USER_CONVIDADO = [
    "  .....YYYYYYY.....  ",
    "  ....YYYYYYYYY....  ",
    "  ....YYYYYYYYY....  ",
    "  .....YYYYYYY.....  ",
    "  ......GGGGG......  ",
    "  ....GGGGGGGGG....  ",
    "  ...GGGGGGGGGGG...  ",
    "  ..GGGGGGGGGGGGG..  ",
    "  ..GGGGGGGGGGGGG..  "
]
PALETA_USER_CONVIDADO = {
    "Y": (220, 180, 120),  # Tom de pele/cabelo neutro
    "G": (80, 110, 90)     # Roupa civil casual
}

# 7. Ícone Desligar (Power Vermelho)
SPRITE_POWER = [
    "  .......RR.......  ",
    "  .......RR.......  ",
    "  ...RR..RR..RR...  ",
    "  ..RR...RR...RR..  ",
    "  ..RR........RR..  ",
    "  ..RR........RR..  ",
    "  ...RR......RR...  ",
    "  ....RRRRRRRR....  "
]
PALETA_POWER = {
    "R": (255, 70, 70)
}

# 8. Logo Oficial: Bug segurando Teclado e Mouse (Preto e Verde)
SPRITE_BUG_TECLADO_MOUSE = [
    "   ..G.....G..   ",
    "   ...G...G...   ",
    "   ..GGGGGGG..   ",
    "   .GG.B.B.GG.   ",
    "   .GGGGGGGGG.   ",
    "   .G.GGGGG.G.   ",
    "   .G.G...G.G.   ",
    "  DDDD.....MMM   ",
    "  DKKD.....MMM   ",
    "  DDDD.....MMM   ",
    "   ..GG.GG..     "
]
PALETA_BUG_TECLADO_MOUSE = {
    "G": (0, 255, 65),     # Verde CyberPixel (#00FF41)
    "D": (10, 95, 31),     # Verde escuro (#0A5F1F)
    "K": (180, 255, 190),  # Teclas do teclado
    "M": (0, 200, 50),     # Mouse
    "B": (0, 0, 0)         # Preto (olhos)
}

# 9. Avatar Pixel Art para o Perfil Simulado do GitHub
SPRITE_GITHUB_AVATAR = [
    "  ....GGGGGG....  ",
    "  ..GGGGGGGGGG..  ",
    "  .GG.BB..BB.GG.  ",
    "  .GG.BB..BB.GG.  ",
    "  .GGGGGGGGGGGG.  ",
    "  .GG.GGGGGG.GG.  ",
    "  ..GG.GGGG.GG..  ",
    "  ....DDDDDD....  ",
    "  ..DDDDDDDDDD..  ",
    "  .DDDDDDDDDDDD.  "
]
PALETA_GITHUB_AVATAR = {
    "G": (0, 255, 65),
    "D": (10, 95, 31),
    "B": (0, 0, 0)
}
