from datetime import datetime
import pygame
from interface.configuracoes import (
    LARGURA_TELA,
    ALTURA_TELA,
    FPS,
    COR_OS_FUNDO,
    COR_OS_VERDE,
    COR_OS_VERDE_ESCURO,
    COR_OS_PAINEL,
    COR_OS_TEXTO_MUTED
)
from interface.pixel_art import (
    desenhar_sprite,
    SPRITE_LIXEIRA,
    PALETA_LIXEIRA,
    SPRITE_NAVEGADOR,
    PALETA_NAVEGADOR,
    SPRITE_PASTA,
    PALETA_PASTA,
    SPRITE_POWER,
    PALETA_POWER,
    SPRITE_BUG_TECLADO_MOUSE,
    PALETA_BUG_TECLADO_MOUSE
)
from interface.janela_xp import JanelaXP
from sistema.arquivos_simulados import reiniciar_sistema_arquivos


class AreaTrabalho:
    def __init__(self, usuario_atual):
        if not pygame.font.get_init():
            pygame.font.init()
        self.usuario = usuario_atual or {"usuario": "convidado", "nome": "Convidado", "perfil": "convidado"}
        
        # Validação estrita de perfil: garante que convidado não herda permissões de admin
        self.eh_admin = (self.usuario.get("perfil") == "admin")

        self.fonte_icone = pygame.font.SysFont("Tahoma, Arial, sans-serif", 12, bold=True)
        self.fonte_relogio = pygame.font.SysFont("Consolas, Tahoma, monospace", 12, bold=True)
        self.fonte_iniciar = pygame.font.SysFont("Trebuchet MS, Arial, sans-serif", 15, bold=True)
        self.fonte_menu = pygame.font.SysFont("Tahoma, Arial, sans-serif", 13)
        self.fonte_menu_header = pygame.font.SysFont("Tahoma, Arial, sans-serif", 14, bold=True)

        # 3 Janelas do sistema
        self.janela_lixeira = JanelaXP("LIXEIRA", "Lixeira", "LIXEIRA", 320, 120, 520, 360)
        self.janela_navegador = JanelaXP("NAVEGADOR", "Cyber Explorer - Laboratório Isolado", "NAVEGADOR", 260, 90, 580, 430)
        self.janela_explorador = JanelaXP("EXPLORADOR", r"C:\Laboratorio\Arquivos", "EXPLORADOR", 200, 100, 600, 430)
        self.janelas = [self.janela_lixeira, self.janela_navegador, self.janela_explorador]

        # Estado do Menu Iniciar
        self.menu_iniciar_aberto = False

        # Posições dos 3 ícones na área de trabalho
        self.icone_lixeira = {"id": "LIXEIRA", "rect": pygame.Rect(30, 30, 80, 75), "nome": "Lixeira", "sprite": SPRITE_LIXEIRA, "paleta": PALETA_LIXEIRA}
        self.icone_navegador = {"id": "NAVEGADOR", "rect": pygame.Rect(30, 130, 80, 75), "nome": "Cyber Explorer", "sprite": SPRITE_NAVEGADOR, "paleta": PALETA_NAVEGADOR}
        self.icone_explorador = {"id": "EXPLORADOR", "rect": pygame.Rect(30, 230, 80, 75), "nome": "Meus Arquivos", "sprite": SPRITE_PASTA, "paleta": PALETA_PASTA}
        self.icones = [self.icone_lixeira, self.icone_navegador, self.icone_explorador]

        # Elementos da Barra de Tarefas
        self.altura_barra = 38
        self.rect_barra = pygame.Rect(0, ALTURA_TELA - self.altura_barra, LARGURA_TELA, self.altura_barra)
        self.rect_btn_iniciar = pygame.Rect(0, ALTURA_TELA - self.altura_barra, 125, self.altura_barra)

    def abrir_janela(self, id_janela):
        """Abre uma das 3 janelas e a traz para o topo."""
        for j in self.janelas:
            if j.id_janela == id_janela:
                j.abrir()
                # Traz para o fim da lista para ser desenhada por último (topo)
                self.janelas.remove(j)
                self.janelas.append(j)
                break

    def executar(self, tela, relogio):
        """
        Executa o loop da Área de Trabalho do convidado.
        Retorna: 'LOGOUT' para voltar à tela de login ou 'DESLIGAR' para fechar.
        """
        resultado_saida = "DESLIGAR"

        try:
            rodando = True
            while rodando:
                pos_mouse = pygame.mouse.get_pos()

                # =============================================================
                # EVENTOS
                # =============================================================
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        resultado_saida = "DESLIGAR"
                        rodando = False
                        break

                    # 1. Primeiro verifica eventos nas janelas ativas (de cima para baixo)
                    tratado_pela_janela = False
                    for j in reversed(self.janelas):
                        if j.processar_evento(evento, pos_mouse):
                            tratado_pela_janela = True
                            break

                    if tratado_pela_janela:
                        continue

                    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        # 2. Clique no Botão Iniciar
                        if self.rect_btn_iniciar.collidepoint(pos_mouse):
                            self.menu_iniciar_aberto = not self.menu_iniciar_aberto
                            continue

                        # 3. Cliques dentro do Menu Iniciar
                        if self.menu_iniciar_aberto:
                            rect_menu = pygame.Rect(0, ALTURA_TELA - self.altura_barra - 310, 270, 310)
                            if rect_menu.collidepoint(pos_mouse):
                                rect_item_arq = pygame.Rect(10, rect_menu.y + 65, 250, 32)
                                rect_item_nav = pygame.Rect(10, rect_menu.y + 105, 250, 32)
                                rect_item_lix = pygame.Rect(10, rect_menu.y + 145, 250, 32)
                                rect_btn_logout = pygame.Rect(10, rect_menu.bottom - 75, 250, 30)
                                rect_btn_desligar = pygame.Rect(10, rect_menu.bottom - 40, 250, 30)

                                if rect_item_arq.collidepoint(pos_mouse):
                                    self.abrir_janela("EXPLORADOR")
                                    self.menu_iniciar_aberto = False
                                elif rect_item_nav.collidepoint(pos_mouse):
                                    self.abrir_janela("NAVEGADOR")
                                    self.menu_iniciar_aberto = False
                                elif rect_item_lix.collidepoint(pos_mouse):
                                    self.abrir_janela("LIXEIRA")
                                    self.menu_iniciar_aberto = False
                                elif rect_btn_logout.collidepoint(pos_mouse):
                                    resultado_saida = "LOGOUT"
                                    rodando = False
                                    break
                                elif rect_btn_desligar.collidepoint(pos_mouse):
                                    resultado_saida = "DESLIGAR"
                                    rodando = False
                                    break
                                continue
                            else:
                                # Clicou fora do menu, fecha o menu
                                self.menu_iniciar_aberto = False

                        # 4. Cliques nos botões da barra de tarefas (restaurar/minimizar)
                        x_tab = 135
                        clicou_tab = False
                        for j in self.janelas:
                            if j.visivel:
                                rect_tab = pygame.Rect(x_tab, ALTURA_TELA - self.altura_barra + 4, 150, 30)
                                if rect_tab.collidepoint(pos_mouse):
                                    j.alternar_minimizar()
                                    if not j.minimizado:
                                        self.janelas.remove(j)
                                        self.janelas.append(j)
                                    clicou_tab = True
                                    break
                                x_tab += 155

                        if clicou_tab:
                            continue

                        # 5. Cliques nos ícones da Área de Trabalho
                        for icone in self.icones:
                            if icone["rect"].collidepoint(pos_mouse):
                                self.abrir_janela(icone["id"])
                                self.menu_iniciar_aberto = False
                                break

                # =============================================================
                # RENDERIZAÇÃO VISUAL (PALETA PRETO E VERDE CYBERPIXEL OS)
                # =============================================================
                # 1. Fundo Preto #000000 com Grade Tecnológica Verde Escuro #0A5F1F
                tela.fill(COR_OS_FUNDO)

                # Grade cibernética sutil de fundo
                altura_util = ALTURA_TELA - self.altura_barra
                for x_grid in range(0, LARGURA_TELA, 40):
                    pygame.draw.line(tela, (5, 30, 12), (x_grid, 0), (x_grid, altura_util), 1)
                for y_grid in range(0, altura_util, 30):
                    pygame.draw.line(tela, (5, 30, 12), (0, y_grid), (LARGURA_TELA, y_grid), 1)

                # Linha de horizonte tecnológico verde escuro na base da área útil
                pygame.draw.line(tela, COR_OS_VERDE_ESCURO, (0, altura_util - 1), (LARGURA_TELA, altura_util - 1), 2)

                # Marca d'água sutil no canto inferior direito
                txt_watermark = self.fonte_icone.render("CyberPixel OS // Laboratório Didático Isolado", True, COR_OS_TEXTO_MUTED)
                tela.blit(txt_watermark, (LARGURA_TELA - txt_watermark.get_width() - 20, altura_util - 22))

                # 2. Ícones da Área de Trabalho
                for icone in self.icones:
                    r_ic = icone["rect"]
                    hover_ic = r_ic.collidepoint(pos_mouse)
                    if hover_ic:
                        surf_h = pygame.Surface((r_ic.width, r_ic.height), pygame.SRCALPHA)
                        surf_h.fill((0, 255, 65, 30))
                        tela.blit(surf_h, (r_ic.x, r_ic.y))
                        pygame.draw.rect(tela, COR_OS_VERDE, r_ic, 1, border_radius=4)

                    # Desenha sprite pixel art do ícone
                    desenhar_sprite(tela, icone["sprite"], icone["paleta"], r_ic.x + 16, r_ic.y + 6, tam_px=2)
                    
                    # Texto do ícone com sombra
                    txt_lbl_sombra = self.fonte_icone.render(icone["nome"], True, (0, 0, 0))
                    tela.blit(txt_lbl_sombra, (r_ic.centerx - txt_lbl_sombra.get_width() // 2 + 1, r_ic.y + 51))
                    txt_lbl = self.fonte_icone.render(icone["nome"], True, (240, 255, 240))
                    tela.blit(txt_lbl, (r_ic.centerx - txt_lbl.get_width() // 2, r_ic.y + 50))

                # 3. Desenhar Janelas Abertas
                for j in self.janelas:
                    j.desenhar(tela)

                # 4. Barra de Tarefas (Paleta Preto e Verde)
                pygame.draw.rect(tela, COR_OS_PAINEL, self.rect_barra)
                # Borda superior verde neon #00FF41
                pygame.draw.line(tela, COR_OS_VERDE, (0, self.rect_barra.y), (LARGURA_TELA, self.rect_barra.y), 2)

                # Botão Iniciar com o Sprite do Bug Teclado e Mouse
                hover_iniciar = self.rect_btn_iniciar.collidepoint(pos_mouse)
                cor_btn_ini = (16, 125, 42) if (hover_iniciar or self.menu_iniciar_aberto) else COR_OS_VERDE_ESCURO
                pygame.draw.rect(tela, cor_btn_ini, self.rect_btn_iniciar, border_radius=4)
                pygame.draw.rect(tela, COR_OS_VERDE, self.rect_btn_iniciar, 1, border_radius=4)
                
                # Sprite do bug segurando mouse e teclado no botão Iniciar
                desenhar_sprite(tela, SPRITE_BUG_TECLADO_MOUSE, PALETA_BUG_TECLADO_MOUSE, self.rect_btn_iniciar.x + 6, self.rect_btn_iniciar.y + 7, tam_px=2)
                tela.blit(self.fonte_iniciar.render("iniciar", True, (255, 255, 255)), (self.rect_btn_iniciar.x + 46, self.rect_btn_iniciar.y + 9))

                # Botões das janelas abertas na Barra de Tarefas
                x_tab = 135
                for j in self.janelas:
                    if j.visivel:
                        rect_tab = pygame.Rect(x_tab, ALTURA_TELA - self.altura_barra + 4, 150, 30)
                        cor_tab = (12, 60, 25) if not j.minimizado else (6, 25, 12)
                        cor_borda_tab = COR_OS_VERDE if not j.minimizado else COR_OS_VERDE_ESCURO
                        pygame.draw.rect(tela, cor_tab, rect_tab, border_radius=3)
                        pygame.draw.rect(tela, cor_borda_tab, rect_tab, 1, border_radius=3)

                        titulo_tab = j.titulo
                        if len(titulo_tab) > 16:
                            titulo_tab = titulo_tab[:14] + ".."
                        tela.blit(self.fonte_icone.render(titulo_tab, True, (220, 255, 220)), (rect_tab.x + 8, rect_tab.y + 8))
                        x_tab += 155

                # Bandeja do Sistema (Systray)
                rect_systray = pygame.Rect(LARGURA_TELA - 200, ALTURA_TELA - self.altura_barra + 4, 195, 30)
                pygame.draw.rect(tela, (6, 24, 12), rect_systray, border_radius=3)
                pygame.draw.rect(tela, COR_OS_VERDE_ESCURO, rect_systray, 1, border_radius=3)

                # Logo marca na barra de tarefas (bug teclado e mouse)
                desenhar_sprite(tela, SPRITE_BUG_TECLADO_MOUSE, PALETA_BUG_TECLADO_MOUSE, rect_systray.x + 6, rect_systray.y + 4, tam_px=2)

                hora_atual = datetime.now().strftime("%H:%M:%S")
                tela.blit(self.fonte_relogio.render(hora_atual, True, COR_OS_VERDE), (rect_systray.x + 42, rect_systray.y + 8))
                tela.blit(self.fonte_icone.render("Convidado", True, COR_OS_TEXTO_MUTED), (rect_systray.x + 115, rect_systray.y + 8))

                # 5. Menu Iniciar (Se Aberto)
                if self.menu_iniciar_aberto:
                    rect_menu = pygame.Rect(0, ALTURA_TELA - self.altura_barra - 310, 270, 310)
                    pygame.draw.rect(tela, COR_OS_PAINEL, rect_menu, border_radius=6)
                    pygame.draw.rect(tela, COR_OS_VERDE, rect_menu, 2, border_radius=6)

                    # Cabeçalho do Menu com Sprite do Bug Teclado e Mouse
                    rect_head = pygame.Rect(0, rect_menu.y, rect_menu.width, 54)
                    pygame.draw.rect(tela, COR_OS_VERDE_ESCURO, rect_head, border_top_left_radius=6, border_top_right_radius=6)
                    pygame.draw.line(tela, COR_OS_VERDE, (0, rect_head.bottom), (rect_menu.width, rect_head.bottom), 1)
                    desenhar_sprite(tela, SPRITE_BUG_TECLADO_MOUSE, PALETA_BUG_TECLADO_MOUSE, rect_head.x + 10, rect_head.y + 6, tam_px=3)
                    tela.blit(self.fonte_menu_header.render("Usuário Convidado", True, (255, 255, 255)), (rect_head.x + 68, rect_head.y + 12))
                    tela.blit(self.fonte_icone.render("Perfil Restrito", True, COR_OS_VERDE), (rect_head.x + 68, rect_head.y + 30))

                    # Itens de Programa
                    itens_menu = [
                        ("Meus Arquivos", SPRITE_PASTA, PALETA_PASTA, rect_menu.y + 65),
                        ("Cyber Explorer", SPRITE_NAVEGADOR, PALETA_NAVEGADOR, rect_menu.y + 105),
                        ("Lixeira", SPRITE_LIXEIRA, PALETA_LIXEIRA, rect_menu.y + 145)
                    ]
                    for nome_m, spr_m, pal_m, y_m in itens_menu:
                        r_item_m = pygame.Rect(8, y_m, rect_menu.width - 16, 32)
                        if r_item_m.collidepoint(pos_mouse):
                            pygame.draw.rect(tela, (14, 55, 25), r_item_m, border_radius=4)
                            pygame.draw.rect(tela, COR_OS_VERDE_ESCURO, r_item_m, 1, border_radius=4)
                        desenhar_sprite(tela, spr_m, pal_m, r_item_m.x + 6, r_item_m.y + 5, tam_px=1)
                        tela.blit(self.fonte_menu.render(nome_m, True, (220, 255, 220)), (r_item_m.x + 36, r_item_m.y + 8))

                    # Barra inferior do Menu Iniciar com 'Encerrar Sessão' e 'Desligar'
                    rect_logout = pygame.Rect(10, rect_menu.bottom - 75, rect_menu.width - 20, 30)
                    hover_logout = rect_logout.collidepoint(pos_mouse)
                    pygame.draw.rect(tela, (130, 80, 15) if hover_logout else (95, 55, 10), rect_logout, border_radius=4)
                    pygame.draw.rect(tela, (255, 175, 40), rect_logout, 1, border_radius=4)
                    tela.blit(self.fonte_icone.render("Encerrar Sessão", True, (255, 240, 220)), (rect_logout.x + 20, rect_logout.y + 8))

                    rect_desligar = pygame.Rect(10, rect_menu.bottom - 40, rect_menu.width - 20, 30)
                    hover_desligar = rect_desligar.collidepoint(pos_mouse)
                    pygame.draw.rect(tela, (150, 25, 25) if hover_desligar else (105, 15, 15), rect_desligar, border_radius=4)
                    pygame.draw.rect(tela, (255, 70, 70), rect_desligar, 1, border_radius=4)
                    desenhar_sprite(tela, SPRITE_POWER, PALETA_POWER, rect_desligar.x + 10, rect_desligar.y + 7, tam_px=2)
                    tela.blit(self.fonte_icone.render("Desligar o Computador", True, (255, 255, 255)), (rect_desligar.x + 40, rect_desligar.y + 8))

                pygame.display.flip()
                relogio.tick(FPS)

        finally:
            # Limpeza: Todas as pastas e arquivos em memória são descartados ao sair
            reiniciar_sistema_arquivos()

        return resultado_saida
