import pygame
from interface.configuracoes import COR_CIANO_NEON, COR_TEXTO, COR_TEXTO_MUTED

# ==========================================
# SESSÃO: COMPONENTES DE INTERFACE (UI)
# ==========================================
class CaixaTexto:
    def __init__(self, x, y, largura, altura, rotulo, somente_leitura=False, somente_digitos=False, prefixo=""):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_ativa = COR_CIANO_NEON
        self.cor_inativa = (40, 58, 85)
        self.cor = self.cor_inativa
        self.texto = ''
        self.rotulo = rotulo
        self.somente_leitura = somente_leitura
        self.somente_digitos = somente_digitos
        self.prefixo = prefixo
        self.ativo = False
        self.fonte = pygame.font.SysFont("Consolas", 14)

    def processar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos) and not self.somente_leitura:
                self.ativo = True
            else:
                self.ativo = False
            self.cor = self.cor_ativa if self.ativo else self.cor_inativa
        
        if evento.type == pygame.KEYDOWN and self.ativo:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif evento.key == pygame.K_TAB:
                pass 
            else:
                char = evento.unicode
                if char and char not in ['´', '`', '~', '^', '¨'] and (not self.somente_digitos or char.isdigit()):
                    self.texto += char

    def desenhar(self, tela):
        pygame.draw.rect(tela, (15, 20, 30), self.rect)
        pygame.draw.rect(tela, self.cor, self.rect, 2)

        texto = self.texto if self.texto else self.rotulo
        if self.prefixo:
            texto = f"Hostname / patrimônio: {self.prefixo}{self.texto or '####'}"
        if self.somente_leitura and self.texto:
            texto = f"{self.rotulo}: {self.texto}"
        cor_texto = COR_TEXTO if self.texto or self.prefixo else COR_TEXTO_MUTED
        largura_util = self.rect.width - 16
        linhas = [""]
        for caractere in texto:
            if caractere == "\n":
                linhas.append("")
                continue
            if self.fonte.size(linhas[-1] + caractere)[0] > largura_util:
                linhas.append(caractere)
            else:
                linhas[-1] += caractere

        total_linhas = max(1, (self.rect.height - 8) // self.fonte.get_linesize())
        linhas_visiveis = linhas[:total_linhas]
        if self.somente_leitura and len(linhas) > total_linhas and len(linhas_visiveis[-1]) > 3:
            linhas_visiveis[-1] = linhas_visiveis[-1][:-3].rstrip() + "..."
        for indice, linha in enumerate(linhas_visiveis):
            img_txt = self.fonte.render(linha, True, cor_texto)
            tela.blit(img_txt, (self.rect.x + 8, self.rect.y + 8 + indice * self.fonte.get_linesize()))

class CaixaSelecao:
    def __init__(self, x, y, largura, altura, rotulo, opcoes, valor_inicial, bloqueado=False, mostrar_rotulo=True, permitir_busca=False):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.rotulo = rotulo
        self.opcoes_base = list(opcoes)
        self.opcoes = list(opcoes)
        self.texto = valor_inicial
        self.ativo = False
        self.bloqueado = bloqueado
        self.mostrar_rotulo = mostrar_rotulo
        self.permitir_busca = permitir_busca
        self.filtro = ""
        self.menu_aberto = False
        self.max_opcoes_visiveis = 7
        self.indice_menu_inicio = 0
        self.indice_destacado = next(
            (indice for indice, (_, valor) in enumerate(opcoes) if valor == valor_inicial),
            0
        )
        self.cor_ativa = COR_CIANO_NEON
        self.cor_inativa = (40, 58, 85)
        self.cor = self.cor_inativa
        self.altura_opcao = 26
        self.fonte = pygame.font.SysFont("Consolas", 14)

    def definir_valor(self, valor):
        valor_normalizado = str(valor).strip().lower()
        for _, valor_opcao in self.opcoes_base:
            if str(valor_opcao).strip().lower() == valor_normalizado:
                self.texto = valor_opcao
                self.indice_destacado = next(
                    indice for indice, (_, valor) in enumerate(self.opcoes_base)
                    if str(valor).strip().lower() == valor_normalizado
                )
                return

    def definir_opcoes(self, opcoes):
        self.opcoes_base = list(opcoes)
        self.definir_filtro(self.filtro)

    def definir_filtro(self, termo):
        self.filtro = str(termo).lstrip()
        if not self.filtro:
            self.opcoes = list(self.opcoes_base)
        else:
            termo_normalizado = self.filtro.casefold()
            self.opcoes = [
                (nome, valor) for nome, valor in self.opcoes_base
                if valor and (
                    termo_normalizado in nome.casefold()
                    or termo_normalizado in str(valor).casefold()
                )
            ]
            if not self.opcoes:
                texto_vazio = "Buscando na NVD..." if len(self.filtro) >= 3 else "Digite 3+ caracteres"
                self.opcoes = [(texto_vazio, "")]
        self.indice_menu_inicio = 0
        self.indice_destacado = min(self.indice_destacado, len(self.opcoes) - 1)

    def limpar_busca(self):
        self.filtro = ""
        self.definir_filtro("")

    def _rect_opcao(self, indice):
        return pygame.Rect(
            self.rect.x,
            self.rect.bottom + indice * self.altura_opcao,
            self.rect.width,
            self.altura_opcao
        )

    def processar_evento(self, evento):
        if self.bloqueado:
            return False

        filtro_anterior = self.filtro

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.menu_aberto:
                opcoes_visiveis = self.opcoes[
                    self.indice_menu_inicio:self.indice_menu_inicio + self.max_opcoes_visiveis
                ]
                for indice_visivel, (_, valor) in enumerate(opcoes_visiveis):
                    if self._rect_opcao(indice_visivel).collidepoint(evento.pos) and valor:
                        indice = self.indice_menu_inicio + indice_visivel
                        self.definir_valor(valor)
                        self.menu_aberto = False
                        self.ativo = True
                        self.cor = self.cor_ativa
                        return False

            self.ativo = self.rect.collidepoint(evento.pos)
            self.cor = self.cor_ativa if self.ativo else self.cor_inativa
            if self.ativo:
                self.menu_aberto = not self.menu_aberto
                if self.menu_aberto and self.permitir_busca:
                    self.texto = ""
                    self.limpar_busca()
            else:
                self.menu_aberto = False

        if evento.type == pygame.KEYDOWN and self.ativo:
            if self.permitir_busca and self.menu_aberto:
                if evento.key == pygame.K_BACKSPACE:
                    self.texto = ""
                    self.definir_filtro(self.filtro[:-1])
                    return self.filtro != filtro_anterior
                if evento.unicode and evento.unicode.isprintable():
                    self.texto = ""
                    self.definir_filtro(self.filtro + evento.unicode)
                    return self.filtro != filtro_anterior

            valores = [valor for _, valor in self.opcoes]
            if not valores:
                return False
            indice_atual = valores.index(self.texto) if self.texto in valores else 0
            if evento.key in (pygame.K_DOWN, pygame.K_UP):
                self.menu_aberto = True
                deslocamento = 1 if evento.key == pygame.K_DOWN else -1
                self.indice_destacado = (indice_atual + deslocamento) % len(valores)
            elif evento.key == pygame.K_RETURN and self.menu_aberto:
                valor = valores[self.indice_destacado]
                if valor:
                    self.definir_valor(valor)
                self.menu_aberto = False
            elif evento.key == pygame.K_ESCAPE:
                self.menu_aberto = False

        if evento.type == pygame.MOUSEWHEEL and self.menu_aberto:
            max_inicio = max(0, len(self.opcoes) - self.max_opcoes_visiveis)
            self.indice_menu_inicio = max(0, min(max_inicio, self.indice_menu_inicio - evento.y))
        return self.filtro != filtro_anterior

    def desenhar(self, tela):
        pygame.draw.rect(tela, (15, 20, 30), self.rect)
        pygame.draw.rect(tela, self.cor, self.rect, 2)

        nome = next((nome for nome, valor in self.opcoes_base if valor == self.texto), "")
        rotulo = f"{self.rotulo}: " if self.mostrar_rotulo else ""
        if self.permitir_busca and self.menu_aberto and self.filtro:
            nome = f"Busca: {self.filtro}"
        texto_exibicao = f"{rotulo}{nome}"
        largura_max = self.rect.width - (28 if not self.bloqueado else 16)
        texto_cortado = texto_exibicao
        while texto_cortado and self.fonte.size(texto_cortado)[0] > largura_max:
            texto_cortado = texto_cortado[:-1]
        if texto_cortado != texto_exibicao and len(texto_cortado) > 3:
            texto_cortado = texto_cortado[:-3].rstrip() + "..."
        texto = self.fonte.render(texto_cortado, True, COR_TEXTO)
        tela.blit(texto, (self.rect.x + 8, self.rect.y + 7))
        if not self.bloqueado:
            seta = self.fonte.render("v", True, self.cor)
            tela.blit(seta, (self.rect.right - seta.get_width() - 8, self.rect.y + 7))

    def desenhar_menu(self, tela):
        if not self.menu_aberto:
            return

        opcoes_visiveis = self.opcoes[
            self.indice_menu_inicio:self.indice_menu_inicio + self.max_opcoes_visiveis
        ]
        if opcoes_visiveis:
            altura_total = len(opcoes_visiveis) * self.altura_opcao
            rect_sombra = pygame.Rect(self.rect.x + 4, self.rect.bottom + 4, self.rect.width, altura_total)
            pygame.draw.rect(tela, (0, 0, 0), rect_sombra)

        pos_mouse = pygame.mouse.get_pos()
        for indice, (nome, _) in enumerate(opcoes_visiveis):
            rect_opcao = self._rect_opcao(indice)
            indice_global = self.indice_menu_inicio + indice
            em_hover = rect_opcao.collidepoint(pos_mouse)
            destacado = (indice_global == self.indice_destacado) or em_hover
            cor_fundo = (10, 28, 18) if destacado else (6, 8, 12)
            cor_borda = self.cor_ativa if destacado else (28, 42, 62)
            pygame.draw.rect(tela, cor_fundo, rect_opcao)
            pygame.draw.rect(tela, cor_borda, rect_opcao, 1)
            nome_visivel = nome
            while nome_visivel and self.fonte.size(nome_visivel)[0] > self.rect.width - 16:
                nome_visivel = nome_visivel[:-1]
            if nome_visivel != nome:
                nome_visivel = nome_visivel.rstrip() + "..."
            texto = self.fonte.render(nome_visivel, True, COR_TEXTO)
            tela.blit(texto, (rect_opcao.x + 8, rect_opcao.y + 5))

        if opcoes_visiveis:
            rect_contorno = pygame.Rect(
                self.rect.x,
                self.rect.bottom,
                self.rect.width,
                len(opcoes_visiveis) * self.altura_opcao
            )
            pygame.draw.rect(tela, self.cor_ativa, rect_contorno, 1)

