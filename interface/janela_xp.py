import pygame
from interface.pixel_art import (
    desenhar_sprite,
    SPRITE_LIXEIRA,
    PALETA_LIXEIRA,
    SPRITE_NAVEGADOR,
    PALETA_NAVEGADOR,
    SPRITE_PASTA,
    PALETA_PASTA,
    SPRITE_GITHUB_AVATAR,
    PALETA_GITHUB_AVATAR
)
from sistema.arquivos_simulados import listar_arquivos, criar_nova_pasta, obter_conteudo


class JanelaXP:
    def __init__(self, id_janela, titulo, tipo_conteudo, x, y, largura=540, altura=380):
        if not pygame.font.get_init():
            pygame.font.init()
        self.id_janela = id_janela
        self.titulo = titulo
        self.tipo_conteudo = tipo_conteudo
        self.rect = pygame.Rect(x, y, largura, altura)
        self.visivel = False
        self.minimizado = False
        self.arrastando = False
        self.offset_x = 0
        self.offset_y = 0

        # Estado para duplo clique e Bloco de Notas
        self.ultimo_clique_tempo = 0
        self.ultimo_item_clicado = None
        self.notepad_aberto = False
        self.notepad_titulo = ""
        self.notepad_conteudo = ""

        # Fontes do sistema
        self.fonte_titulo = pygame.font.SysFont("Tahoma, Arial, sans-serif", 13, bold=True)
        self.fonte_texto = pygame.font.SysFont("Tahoma, Arial, sans-serif", 13)
        self.fonte_texto_bold = pygame.font.SysFont("Tahoma, Arial, sans-serif", 13, bold=True)
        self.fonte_mono = pygame.font.SysFont("Consolas, Courier New", 12)
        self.fonte_mini = pygame.font.SysFont("Tahoma, Arial, sans-serif", 11)

    def abrir(self):
        self.visivel = True
        self.minimizado = False

    def fechar(self):
        self.visivel = False
        self.arrastando = False
        self.notepad_aberto = False

    def alternar_minimizar(self):
        self.minimizado = not self.minimizado

    def processar_evento(self, evento, pos_mouse):
        if not self.visivel or self.minimizado:
            return False

        rect_barra_titulo = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 28)
        rect_btn_fechar = pygame.Rect(self.rect.right - 26, self.rect.y + 4, 20, 20)
        rect_btn_minimizar = pygame.Rect(self.rect.right - 50, self.rect.y + 4, 20, 20)

        # Se o Bloco de Notas simulado estiver aberto (sub-janela do Explorador)
        if self.notepad_aberto:
            rect_np = pygame.Rect(self.rect.x + 30, self.rect.y + 40, self.rect.width - 60, self.rect.height - 60)
            rect_np_fechar = pygame.Rect(rect_np.right - 24, rect_np.y + 4, 18, 18)
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_np_fechar.collidepoint(pos_mouse):
                    self.notepad_aberto = False
                    return True
                if rect_np.collidepoint(pos_mouse):
                    return True

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if rect_btn_fechar.collidepoint(pos_mouse):
                self.fechar()
                return True

            if rect_btn_minimizar.collidepoint(pos_mouse):
                self.alternar_minimizar()
                return True

            if rect_barra_titulo.collidepoint(pos_mouse):
                self.arrastando = True
                self.offset_x = pos_mouse[0] - self.rect.x
                self.offset_y = pos_mouse[1] - self.rect.y
                return True

            # Ações dentro do Explorador de Arquivos
            if self.tipo_conteudo == "EXPLORADOR":
                rect_corpo = pygame.Rect(self.rect.x + 8, self.rect.y + 34, self.rect.width - 16, self.rect.height - 42)
                rect_btn_nova_pasta = pygame.Rect(rect_corpo.x + 8, rect_corpo.y + 36, 120, 24)

                # Clique em "+ Nova pasta"
                if rect_btn_nova_pasta.collidepoint(pos_mouse):
                    criar_nova_pasta()
                    return True

                # Cliques e Duplo Clique nos arquivos da lista
                agora = pygame.time.get_ticks()
                itens = listar_arquivos()
                for idx, item in enumerate(itens):
                    y_item = rect_corpo.y + 92 + (idx * 24)
                    r_item = pygame.Rect(rect_corpo.x + 8, y_item, rect_corpo.width - 16, 24)
                    if r_item.collidepoint(pos_mouse):
                        # Detecta duplo clique (intervalo menor que 400ms no mesmo item)
                        if self.ultimo_item_clicado == item["nome"] and (agora - self.ultimo_clique_tempo) < 400:
                            if item["nome"].endswith(".txt"):
                                self.notepad_aberto = True
                                self.notepad_titulo = item["nome"]
                                self.notepad_conteudo = obter_conteudo(item["nome"])
                            self.ultimo_item_clicado = None
                        else:
                            self.ultimo_item_clicado = item["nome"]
                            self.ultimo_clique_tempo = agora
                        return True

            if self.rect.collidepoint(pos_mouse):
                return True

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastando = False

        elif evento.type == pygame.MOUSEMOTION:
            if self.arrastando:
                self.rect.x = max(0, min(1280 - self.rect.width, pos_mouse[0] - self.offset_x))
                self.rect.y = max(0, min(720 - 40 - self.rect.height, pos_mouse[1] - self.offset_y))
                return True

        return False

    def desenhar(self, tela):
        if not self.visivel or self.minimizado:
            return

        pos_mouse = pygame.mouse.get_pos()

        # Sombra e Moldura Clássica
        rect_sombra = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height)
        sombra_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        sombra_surf.fill((0, 0, 0, 50))
        tela.blit(sombra_surf, (rect_sombra.x, rect_sombra.y))

        pygame.draw.rect(tela, (236, 233, 216), self.rect, border_radius=4)
        pygame.draw.rect(tela, (0, 85, 230), self.rect, 3, border_radius=4)

        # Barra de Título Azul com Gradiente
        rect_barra = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width - 6, 26)
        for i in range(rect_barra.height):
            fator = i / rect_barra.height
            r = int(0 + 20 * fator)
            g = int(85 + 60 * fator)
            b = int(230 + 15 * fator)
            pygame.draw.line(tela, (r, g, b), (rect_barra.x, rect_barra.y + i), (rect_barra.right, rect_barra.y + i))

        # Ícone no topo da janela
        if self.tipo_conteudo == "LIXEIRA":
            desenhar_sprite(tela, SPRITE_LIXEIRA, PALETA_LIXEIRA, rect_barra.x + 6, rect_barra.y + 5, tam_px=1)
        elif self.tipo_conteudo == "NAVEGADOR":
            desenhar_sprite(tela, SPRITE_NAVEGADOR, PALETA_NAVEGADOR, rect_barra.x + 6, rect_barra.y + 5, tam_px=1)
        else:
            desenhar_sprite(tela, SPRITE_PASTA, PALETA_PASTA, rect_barra.x + 6, rect_barra.y + 5, tam_px=1)

        tela.blit(self.fonte_titulo.render(self.titulo, True, (255, 255, 255)), (rect_barra.x + 28, rect_barra.y + 5))

        # Botão Fechar [X]
        rect_btn_fechar = pygame.Rect(self.rect.right - 26, self.rect.y + 5, 20, 20)
        hover_fechar = rect_btn_fechar.collidepoint(pos_mouse)
        pygame.draw.rect(tela, (230, 60, 60) if hover_fechar else (210, 40, 40), rect_btn_fechar, border_radius=3)
        pygame.draw.rect(tela, (255, 255, 255), rect_btn_fechar, 1, border_radius=3)
        tela.blit(self.fonte_titulo.render("X", True, (255, 255, 255)), (rect_btn_fechar.x + 5, rect_btn_fechar.y + 2))

        # Botão Minimizar [-]
        rect_btn_minimizar = pygame.Rect(self.rect.right - 50, self.rect.y + 5, 20, 20)
        hover_min = rect_btn_minimizar.collidepoint(pos_mouse)
        pygame.draw.rect(tela, (50, 110, 200) if hover_min else (30, 85, 170), rect_btn_minimizar, border_radius=3)
        pygame.draw.rect(tela, (255, 255, 255), rect_btn_minimizar, 1, border_radius=3)
        tela.blit(self.fonte_titulo.render("_", True, (255, 255, 255)), (rect_btn_minimizar.x + 6, rect_btn_minimizar.y - 4))

        # Área Interna da Janela
        rect_corpo = pygame.Rect(self.rect.x + 8, self.rect.y + 34, self.rect.width - 16, self.rect.height - 42)
        pygame.draw.rect(tela, (255, 255, 255), rect_corpo)
        pygame.draw.rect(tela, (120, 120, 120), rect_corpo, 1)

        # =====================================================================
        # 1. CONTEÚDO: LIXEIRA
        # =====================================================================
        if self.tipo_conteudo == "LIXEIRA":
            desenhar_sprite(tela, SPRITE_LIXEIRA, PALETA_LIXEIRA, rect_corpo.centerx - 24, rect_corpo.y + 60, tam_px=3)
            txt_vazia = self.fonte_texto_bold.render("A Lixeira está vazia.", True, (50, 50, 50))
            tela.blit(txt_vazia, (rect_corpo.centerx - txt_vazia.get_width() // 2, rect_corpo.y + 140))
            txt_detalhe = self.fonte_texto.render("Nenhum item descartado no momento.", True, (120, 120, 120))
            tela.blit(txt_detalhe, (rect_corpo.centerx - txt_detalhe.get_width() // 2, rect_corpo.y + 170))

        # =====================================================================
        # 2. CONTEÚDO: CYBER EXPLORER - PERFIL GITHUB SIMULADO
        # =====================================================================
        elif self.tipo_conteudo == "NAVEGADOR":
            # Barra de Endereço Clássica
            rect_url = pygame.Rect(rect_corpo.x + 8, rect_corpo.y + 8, rect_corpo.width - 16, 26)
            pygame.draw.rect(tela, (245, 245, 245), rect_url)
            pygame.draw.rect(tela, (180, 180, 180), rect_url, 1)
            tela.blit(self.fonte_mono.render("Endereco: https://github.com/parcos7", True, (30, 30, 30)), (rect_url.x + 8, rect_url.y + 5))

            # Área do Perfil Simulado (Fundo cinza claro estilo página de perfil)
            rect_perfil = pygame.Rect(rect_corpo.x + 8, rect_corpo.y + 40, rect_corpo.width - 16, rect_corpo.height - 75)
            pygame.draw.rect(tela, (250, 251, 253), rect_perfil)
            pygame.draw.rect(tela, (215, 220, 230), rect_perfil, 1)

            # Avatar em Pixel Art Próprio
            desenhar_sprite(tela, SPRITE_GITHUB_AVATAR, PALETA_GITHUB_AVATAR, rect_perfil.x + 20, rect_perfil.y + 20, tam_px=4)

            # Informações do Usuário
            tela.blit(self.fonte_texto_bold.render("parcos7", True, (20, 20, 20)), (rect_perfil.x + 105, rect_perfil.y + 20))
            tela.blit(self.fonte_texto.render("Estudante de Cibersegurança | UFU", True, (70, 70, 70)), (rect_perfil.x + 105, rect_perfil.y + 42))
            tela.blit(self.fonte_mini.render("Foco: Defesa Cibernética, Python, Containers e Análise Linear de Risco.", True, (90, 90, 90)), (rect_perfil.x + 105, rect_perfil.y + 64))

            # Divisória
            pygame.draw.line(tela, (220, 225, 235), (rect_perfil.x + 15, rect_perfil.y + 95), (rect_perfil.right - 15, rect_perfil.y + 95), 1)

            # Repositórios (Lista vazia até a definição dos nomes reais)
            tela.blit(self.fonte_texto_bold.render("Repositórios em Destaque:", True, (40, 40, 40)), (rect_perfil.x + 20, rect_perfil.y + 105))

            repos = []

            if not repos:
                txt_vazio = self.fonte_texto.render("Nenhum repositório público listado no momento.", True, (120, 120, 120))
                tela.blit(txt_vazio, (rect_perfil.x + 20, rect_perfil.y + 135))
            else:
                for i, (repo_nome, repo_desc) in enumerate(repos):
                    y_repo = rect_perfil.y + 130 + (i * 48)
                    rect_card_repo = pygame.Rect(rect_perfil.x + 20, y_repo, rect_perfil.width - 40, 42)
                    pygame.draw.rect(tela, (255, 255, 255), rect_card_repo, border_radius=4)
                    pygame.draw.rect(tela, (200, 210, 225), rect_card_repo, 1, border_radius=4)
                    tela.blit(self.fonte_texto_bold.render(repo_nome, True, (0, 85, 200)), (rect_card_repo.x + 10, rect_card_repo.y + 4))
                    tela.blit(self.fonte_mini.render(repo_desc, True, (60, 60, 60)), (rect_card_repo.x + 10, rect_card_repo.y + 22))

            # Rodapé Obrigatório
            txt_rodape = self.fonte_mini.render("Conteúdo simulado. Laboratório sem conexão real.", True, (130, 130, 130))
            tela.blit(txt_rodape, (rect_corpo.centerx - txt_rodape.get_width() // 2, rect_corpo.bottom - 22))

        # =====================================================================
        # 3. CONTEÚDO: EXPLORADOR DE ARQUIVOS
        # =====================================================================
        elif self.tipo_conteudo == "EXPLORADOR":
            # Barra de Endereço
            rect_caminho = pygame.Rect(rect_corpo.x + 8, rect_corpo.y + 6, rect_corpo.width - 16, 24)
            pygame.draw.rect(tela, (245, 245, 245), rect_caminho)
            pygame.draw.rect(tela, (180, 180, 180), rect_caminho, 1)
            tela.blit(self.fonte_mono.render(r"Endereco: C:\Laboratorio\Arquivos", True, (40, 40, 40)), (rect_caminho.x + 6, rect_caminho.y + 4))

            # Barra de Ferramentas com botão "Nova pasta"
            rect_btn_nova_pasta = pygame.Rect(rect_corpo.x + 8, rect_corpo.y + 36, 120, 24)
            hover_np = rect_btn_nova_pasta.collidepoint(pos_mouse)
            pygame.draw.rect(tela, (225, 235, 245) if hover_np else (240, 240, 245), rect_btn_nova_pasta, border_radius=3)
            pygame.draw.rect(tela, (100, 140, 190), rect_btn_nova_pasta, 1, border_radius=3)
            tela.blit(self.fonte_texto_bold.render("+ Nova pasta", True, (20, 50, 100)), (rect_btn_nova_pasta.x + 12, rect_btn_nova_pasta.y + 4))

            # Dica visual
            tela.blit(self.fonte_mini.render("[ Dica: Duplo clique em arquivos .txt para abrir no Bloco de Notas ]", True, (100, 100, 100)), (rect_btn_nova_pasta.right + 15, rect_btn_nova_pasta.y + 5))

            # Cabeçalho da Listagem
            pygame.draw.rect(tela, (235, 240, 245), (rect_corpo.x + 8, rect_corpo.y + 66, rect_corpo.width - 16, 22))
            tela.blit(self.fonte_texto_bold.render("Nome", True, (50, 50, 50)), (rect_corpo.x + 14, rect_corpo.y + 69))
            tela.blit(self.fonte_texto_bold.render("Tipo", True, (50, 50, 50)), (rect_corpo.x + 280, rect_corpo.y + 69))
            tela.blit(self.fonte_texto_bold.render("Tamanho", True, (50, 50, 50)), (rect_corpo.x + 420, rect_corpo.y + 69))

            # Lista Dinâmica de Arquivos em Memória
            itens = listar_arquivos()
            for idx, item in enumerate(itens[:10]):
                y_item = rect_corpo.y + 92 + (idx * 24)
                r_item_linha = pygame.Rect(rect_corpo.x + 8, y_item, rect_corpo.width - 16, 24)
                hover_item = r_item_linha.collidepoint(pos_mouse)

                if hover_item:
                    pygame.draw.rect(tela, (220, 235, 255), r_item_linha)
                elif idx % 2 == 1:
                    pygame.draw.rect(tela, (248, 250, 252), r_item_linha)

                if item["eh_pasta"]:
                    desenhar_sprite(tela, SPRITE_PASTA, PALETA_PASTA, rect_corpo.x + 14, y_item + 2, tam_px=1)
                else:
                    pygame.draw.rect(tela, (200, 215, 230), (rect_corpo.x + 16, y_item + 3, 13, 15))
                    pygame.draw.rect(tela, (80, 110, 140), (rect_corpo.x + 16, y_item + 3, 13, 15), 1)

                tela.blit(self.fonte_texto.render(item["nome"], True, (30, 30, 30)), (rect_corpo.x + 38, y_item + 3))
                tela.blit(self.fonte_texto.render(item["tipo"], True, (90, 90, 90)), (rect_corpo.x + 280, y_item + 3))
                tela.blit(self.fonte_texto.render(item["tamanho"], True, (90, 90, 90)), (rect_corpo.x + 420, y_item + 3))

            # Bloco de Notas Simulado (Sub-janela quando abre um .txt)
            if self.notepad_aberto:
                rect_np = pygame.Rect(self.rect.x + 25, self.rect.y + 35, self.rect.width - 50, self.rect.height - 50)
                pygame.draw.rect(tela, (245, 245, 245), rect_np, border_radius=4)
                pygame.draw.rect(tela, (0, 70, 180), rect_np, 2, border_radius=4)

                # Barra de título do Bloco de Notas
                rect_np_barra = pygame.Rect(rect_np.x, rect_np.y, rect_np.width, 24)
                pygame.draw.rect(tela, (0, 70, 180), rect_np_barra, border_top_left_radius=4, border_top_right_radius=4)
                tela.blit(self.fonte_titulo.render(f"Bloco de Notas - {self.notepad_titulo}", True, (255, 255, 255)), (rect_np.x + 10, rect_np.y + 4))

                rect_np_fechar = pygame.Rect(rect_np.right - 22, rect_np.y + 3, 18, 18)
                pygame.draw.rect(tela, (210, 40, 40), rect_np_fechar, border_radius=2)
                tela.blit(self.fonte_mini.render("X", True, (255, 255, 255)), (rect_np_fechar.x + 5, rect_np_fechar.y + 2))

                # Área de Texto do Arquivo
                rect_np_texto = pygame.Rect(rect_np.x + 8, rect_np.y + 30, rect_np.width - 16, rect_np.height - 38)
                pygame.draw.rect(tela, (255, 255, 255), rect_np_texto)
                pygame.draw.rect(tela, (180, 180, 180), rect_np_texto, 1)

                linhas_txt = self.notepad_conteudo.split("\n")
                for l_idx, l_texto in enumerate(linhas_txt[:16]):
                    tela.blit(self.fonte_mono.render(l_texto, True, (20, 20, 20)), (rect_np_texto.x + 8, rect_np_texto.y + 6 + (l_idx * 16)))
