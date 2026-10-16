import sys
import math
import random
import datetime
import time
import pygame
from ativos import Equipamento
from persistencia import ler_db
from CRUD.cadastro import cadastrar_ativo
from CRUD.atualizar import atualizar_ativo
from CRUD.remover import remover_ativo
from vulnerabilidades import CATALOGO_VULNERABILIDADES, registrar_vulnerabilidade, corrigir_vulnerabilidade
from CRUD.risco_salas import calcular_relatorio_risco_por_sala
from integracoes.nvd_api import NvdCveSearchWorker

# ==========================================
# SESSÃO: CONFIGURAÇÕES GERAIS E CONSTANTES
# ==========================================
LARGURA_TELA = 1280
ALTURA_TELA = 720
TITULO_JANELA = "CyberPixel - SOC Level 3 [Visual Interface]"
FPS = 50

# --- TEMA DARK ---
COR_FUNDO = (0, 0, 0)
COR_CHAO = (5, 5, 5)
COR_GRADE = (0, 40, 0)
COR_PAREDE = (0, 0, 0)
COR_TEXTO = (0, 255, 0)
COR_TEXTO_MUTED = (0, 150, 0)
COR_CIANO_NEON = (0, 255, 0)
COR_VERDE_MATRIX = (0, 255, 0)

# --- ESCALA CROMÁTICA DE ALERTAS E RISCO ---
COR_AMBAR = (200, 200, 0)              # Risco Baixo
COR_LARANJA = (255, 140, 0)            # Risco Médio
COR_VERMELHO_CLARO = (255, 80, 80)     # Risco Alto
COR_VERMELHO_ESCURO = (180, 0, 0)      # Risco Crítico
COR_VERMELHO_NEON = (255, 0, 0)        # Interface Padrão

COR_PAINEL = (0, 0, 0)
COR_PAINEL_BORDA = (0, 255, 0)

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
        for indice, linha in enumerate(linhas[:total_linhas]):
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
        texto = self.fonte.render(f"{rotulo}{nome}", True, COR_TEXTO)
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
        for indice, (nome, _) in enumerate(opcoes_visiveis):
            rect_opcao = self._rect_opcao(indice)
            indice_global = self.indice_menu_inicio + indice
            cor_borda = self.cor_ativa if indice_global == self.indice_destacado else self.cor_inativa
            pygame.draw.rect(tela, (15, 20, 30), rect_opcao)
            pygame.draw.rect(tela, cor_borda, rect_opcao, 1)
            nome_visivel = nome
            while nome_visivel and self.fonte.size(nome_visivel)[0] > self.rect.width - 16:
                nome_visivel = nome_visivel[:-1]
            if nome_visivel != nome:
                nome_visivel = nome_visivel.rstrip() + "..."
            texto = self.fonte.render(nome_visivel, True, COR_TEXTO)
            tela.blit(texto, (rect_opcao.x + 8, rect_opcao.y + 5))

# ==========================================
# SESSÃO: CLASSE PRINCIPAL DO SISTEMA (APP)
# ==========================================
class App:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(200, 50) 
        
        self.servidor_foco_painel = None

        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JANELA)
        self.relogio = pygame.time.Clock()
        self.rodando = True

        self.fonte_p = pygame.font.SysFont("Consolas", 14)
        self.fonte_m = pygame.font.SysFont("Consolas", 16, bold=True)
        self.fonte_g = pygame.font.SysFont("Consolas", 24, bold=True)
        self.fonte_emoji = pygame.font.SysFont("Segoe UI Emoji", 26)

        self.rect_notebook = pygame.Rect(490, 470, 180, 100)
        self.rect_servidor = pygame.Rect(1020, 160, 200, 480)
        self.rect_workstation = pygame.Rect(140, 400, 190, 160)
        self.rect_telao = pygame.Rect(430, 90, 420, 200)

        self.modal_ativo = None          
        self.objeto_em_hover = None      
        self.aba_crud_ativa = "LISTAR"   

        self.alerta_ativo = False
        self.cor_alerta_atual = COR_VERDE_MATRIX
        self.nivel_alerta_str = "SEGURO"
        
        self.lista_ativos_display = []
        self.ativos_brutos = [] 
        self.relatorio_risco = []
        
        self.lista_vulns_ativas = []
        self.rects_vulns = []
        self.rects_ativos_vuln = []
        self.rects_matriz_risco = []
        self.rects_ativos_crud = []
        self.scroll_resultados_consulta = 0
        
        self.historico_logs = []
        self.scroll_logs = 0
        self.scroll_crud_ativos = 0
        self.scroll_vuln_inv = 0
        self.scroll_vuln_lista = 0
        self.scroll_gaveta_servidores = 0
        self.log_selecionado = None
        self.rects_logs = []
        
        caracteres_matriz = ['0', '1', 'A', 'B', 'C', 'D', 'E', 'F', 'X']
        self.bg_drops = []
        for _ in range(120): 
            self.bg_drops.append({
                'x': random.randint(0, LARGURA_TELA),
                'y': random.randint(-ALTURA_TELA, ALTURA_TELA),
                'speed': random.uniform(1.0, 3.5),
                'char': random.choice(caracteres_matriz)
            })
        
        self.mensagem_status = ""
        self.cor_status = COR_TEXTO
        
        self.prefixos_hostname = {
            "NOTEBOOK": "notp",
            "SERVIDOR": "serv",
            "DESKTOP": "micp",
            "ROTEADOR": "rotp"
        }
        self.cad_tipo = CaixaSelecao(
            300, 175, 300, 28, "Tipo de ativo",
            [("Notebook", "NOTEBOOK"), ("Servidor", "SERVIDOR"), ("Desktop", "DESKTOP"), ("Roteador", "ROTEADOR")],
            "NOTEBOOK"
        )
        self.cad_host = CaixaTexto(300, 220, 300, 28, "Sufixo do hostname", somente_digitos=True, prefixo="notp")
        self.cad_resp = CaixaTexto(300, 265, 300, 28, "Responsável (Sem números)")
        opcoes_salas = [(f"Sala {letra}", f"Sala {letra}") for letra in "ABCD"]
        opcoes_salas.append(("+ Nova sala...", "__NOVA_SALA__"))
        self.cad_loc = CaixaSelecao(300, 310, 300, 28, "Localidade", opcoes_salas, "Sala A")
        self.cad_sala_nova = CaixaTexto(300, 310, 300, 28, "Nome da nova sala")
        self.cad_extra = CaixaTexto(300, 355, 300, 28, "Dado Extra (SO, RAM ou FW)")
        self.campos_cad = [self.cad_tipo, self.cad_host, self.cad_resp, self.cad_loc, self.cad_extra]
        self._atualizar_rotulo_dado_extra()

        self.upd_id = CaixaTexto(300, 200, 300, 32, "ID ou Hostname do Ativo")
        self.upd_resp = CaixaTexto(300, 250, 300, 32, "Novo Responsável (Opcional)")
        self.upd_loc = CaixaTexto(300, 300, 300, 32, "Nova Localidade (Opcional)")
        self.campos_upd = [self.upd_id, self.upd_resp, self.upd_loc]

        self.rem_id = CaixaTexto(300, 250, 300, 32, "ID ou Hostname do Ativo")
        self.campos_rem = [self.rem_id]
        self.consulta_busca = CaixaTexto(300, 175, 690, 28, "Buscar usuário, hostname ou patrimônio")
        self.ativo_consulta_selecionado = None

        opcoes_vulnerabilidade = [("Selecione uma vulnerabilidade", "")]
        opcoes_vulnerabilidade.extend((item['nome'], item['id']) for item in CATALOGO_VULNERABILIDADES)
        self.vuln_id = CaixaTexto(280, 160, 300, 28, "ID ou Hostname do Alvo", somente_leitura=True)
        self.vuln_modelo = CaixaSelecao(280, 200, 300, 28, "Vulnerabilidade", opcoes_vulnerabilidade, "", mostrar_rotulo=False, permitir_busca=True)
        self.vuln_cve = CaixaTexto(280, 240, 300, 28, "CVE", somente_leitura=True)
        self.vuln_desc = CaixaTexto(280, 280, 300, 28, "Descrição", somente_leitura=True)
        self.vuln_cat = CaixaTexto(280, 320, 300, 28, "Categoria", somente_leitura=True)
        opcoes_severidade = [("Aguardando padrão", "")] + [(nome, valor) for nome, valor in [("Baixa", "baixa"), ("Média", "media"), ("Alta", "alta"), ("Crítica", "critica")]]
        self.vuln_sev = CaixaSelecao(280, 360, 300, 28, "Severidade", opcoes_severidade, "", bloqueado=True)
        self.vuln_stat = CaixaSelecao(280, 400, 300, 28, "Status", [("Aberto", Equipamento.STATUS_ABERTO), ("Fechado", Equipamento.STATUS_FECHADO)], Equipamento.STATUS_ABERTO, bloqueado=True)
        self.vuln_log = CaixaTexto(280, 440, 300, 56, "Log da Correção (Obrigatório p/ Corrigir)")
        self.campos_vuln = [self.vuln_id, self.vuln_modelo, self.vuln_cve, self.vuln_desc, self.vuln_cat, self.vuln_sev, self.vuln_stat, self.vuln_log]
        self.vulnerabilidades_disponiveis = {item['id']: item for item in CATALOGO_VULNERABILIDADES}
        self.resultados_nvd = []
        self.total_resultados_nvd = 0
        self.proximo_indice_nvd = 0
        self.busca_nvd_pendente = ""
        self.busca_nvd_inicio_pendente = 0
        self.busca_nvd_disparar_em = 0.0
        self.worker_nvd = NvdCveSearchWorker()

        self.adicionar_log("SISTEMA", "SOC", "Interface de Segurança Nível 3 Inicializada.")
        self.sincronizar_dados()

    # ==========================================
    # SUB-SESSÃO: GERENCIAMENTO DE ESTADO E DADOS
    # ==========================================
    def adicionar_log(self, acao, alvo, detalhes):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.historico_logs.insert(0, {
            "hora": hora,
            "acao": acao.upper(),
            "alvo": alvo,
            "detalhes": detalhes
        })

    def definir_mensagem(self, texto, cor):
        self.mensagem_status = texto
        self.cor_status = cor

    def preencher_vulnerabilidade_predefinida(self, identificador):
        vulnerabilidade = self.vulnerabilidades_disponiveis.get(identificador)
        if vulnerabilidade is None:
            self.vuln_cve.texto = ""
            self.vuln_desc.texto = ""
            self.vuln_cat.texto = ""
            self.vuln_sev.definir_valor("")
            self.vuln_stat.definir_valor(Equipamento.STATUS_ABERTO)
            return

        self.vuln_cve.texto = vulnerabilidade['cve']
        self.vuln_desc.texto = vulnerabilidade['descricao']
        self.vuln_cat.texto = vulnerabilidade['categoria']
        ativo_alvo = next(
            (ativo for ativo in self.ativos_brutos if str(ativo.get('id', '')) == self.vuln_id.texto),
            None
        )
        severidade = vulnerabilidade['severidade']
        if ativo_alvo and str(ativo_alvo.get('tipo', '')).upper() == "SERVIDOR":
            severidade = "critica"
        self.vuln_sev.definir_valor(severidade)
        self.vuln_stat.definir_valor(Equipamento.STATUS_ABERTO)

    def _atualizar_opcoes_catalogo(self):
        opcoes = [("Selecione uma vulnerabilidade", "")]
        opcoes.extend((item['nome'], item['id']) for item in CATALOGO_VULNERABILIDADES)
        cves_locais = {item['cve'].upper() for item in CATALOGO_VULNERABILIDADES if item['cve'] != 'N/A'}
        opcoes.extend(
            (item['nome'], item['id'])
            for item in self.resultados_nvd
            if item['cve'].upper() not in cves_locais
        )
        if len(self.resultados_nvd) < self.total_resultados_nvd:
            opcoes.append((f"Mais resultados NVD: {self.vuln_modelo.filtro}", "__NVD_MORE__"))
        self.vuln_modelo.definir_opcoes(opcoes)

    def _programar_busca_nvd(self, termo):
        termo = str(termo).strip()
        self.resultados_nvd = []
        self.total_resultados_nvd = 0
        self.proximo_indice_nvd = 0
        self.vulnerabilidades_disponiveis = {item['id']: item for item in CATALOGO_VULNERABILIDADES}
        self._atualizar_opcoes_catalogo()

        if len(termo) < 3:
            self.busca_nvd_pendente = ""
            self.definir_mensagem("Digite 3+ caracteres para buscar na NVD.", COR_AMBAR)
            return

        self.busca_nvd_pendente = termo
        self.busca_nvd_inicio_pendente = 0
        self.busca_nvd_disparar_em = time.monotonic() + 0.6
        self.definir_mensagem("Buscando na NVD...", COR_CIANO_NEON)

    def _programar_proxima_pagina_nvd(self):
        self.busca_nvd_pendente = self.vuln_modelo.filtro.strip()
        self.busca_nvd_inicio_pendente = self.proximo_indice_nvd
        self.busca_nvd_disparar_em = time.monotonic()
        self.vuln_modelo.menu_aberto = True
        self.definir_mensagem("Carregando mais CVEs da NVD...", COR_CIANO_NEON)

    def _processar_busca_nvd(self):
        resultado = self.worker_nvd.receber()
        if resultado:
            termo, pagina, erro = resultado
            busca_atual = self.vuln_modelo.filtro.strip()
            if termo.casefold() == busca_atual.casefold() and self.vuln_modelo.menu_aberto:
                if erro:
                    self.definir_mensagem("NVD indisponível; busca local mantida.", COR_AMBAR)
                else:
                    vulnerabilidades = pagina['vulnerabilidades']
                    inicio = pagina['inicio']
                    if inicio == 0:
                        self.resultados_nvd = []
                    ids_existentes = {item['id'] for item in self.resultados_nvd}
                    self.resultados_nvd.extend(
                        item for item in vulnerabilidades
                        if item['id'] not in ids_existentes
                    )
                    self.total_resultados_nvd = pagina['total']
                    self.proximo_indice_nvd = inicio + len(vulnerabilidades)
                    self.vulnerabilidades_disponiveis = {
                        item['id']: item
                        for item in (*CATALOGO_VULNERABILIDADES, *self.resultados_nvd)
                    }
                    self._atualizar_opcoes_catalogo()
                    mensagem = f"NVD: {len(self.resultados_nvd)} de {self.total_resultados_nvd}."
                    self.definir_mensagem(mensagem, COR_CIANO_NEON)

        if (
            self.busca_nvd_pendente
            and time.monotonic() >= self.busca_nvd_disparar_em
        ):
            self.worker_nvd.solicitar(self.busca_nvd_pendente, self.busca_nvd_inicio_pendente)
            self.busca_nvd_pendente = ""

    def _limpar_busca_nvd(self):
        self.busca_nvd_pendente = ""
        self.resultados_nvd = []
        self.total_resultados_nvd = 0
        self.proximo_indice_nvd = 0
        self.busca_nvd_inicio_pendente = 0
        self.vulnerabilidades_disponiveis = {item['id']: item for item in CATALOGO_VULNERABILIDADES}
        opcoes = [("Selecione uma vulnerabilidade", "")]
        opcoes.extend((item['nome'], item['id']) for item in CATALOGO_VULNERABILIDADES)
        self.vuln_modelo.definir_opcoes(opcoes)
        self.vuln_modelo.limpar_busca()
        self.vuln_modelo.definir_valor("")

    def _atualizar_rotulo_dado_extra(self):
        rotulos = {
            "NOTEBOOK": "Memória RAM (GB)",
            "DESKTOP": "Memória RAM (GB)",
            "SERVIDOR": "Sistema operacional",
            "ROTEADOR": "Firmware atualizado? (S/N)"
        }
        self.cad_extra.rotulo = rotulos.get(self.cad_tipo.texto, "Dado extra")

    def _atualizar_opcoes_salas(self):
        salas = [f"Sala {letra}" for letra in "ABCD"]
        salas_existentes = {
            str(ativo.get('local', '')).strip()
            for ativo in self.ativos_brutos
            if str(ativo.get('local', '')).strip()
        }
        salas.extend(sorted(
            (sala for sala in salas_existentes if sala.casefold() not in {item.casefold() for item in salas}),
            key=str.casefold
        ))
        opcoes = [(sala, sala) for sala in salas]
        opcoes.append(("+ Nova sala...", "__NOVA_SALA__"))
        valor_atual = self.cad_loc.texto
        self.cad_loc.definir_opcoes(opcoes)
        if valor_atual not in {valor for _, valor in opcoes}:
            valor_atual = "Sala A"
        self.cad_loc.definir_valor(valor_atual)

    def _campos_cadastro_ativos(self):
        campo_local = self.cad_sala_nova if self.cad_loc.texto == "__NOVA_SALA__" else self.cad_loc
        return [self.cad_tipo, self.cad_host, self.cad_resp, campo_local, self.cad_extra]

    def _localidade_cadastro(self):
        if self.cad_loc.texto == "__NOVA_SALA__":
            return self.cad_sala_nova.texto.strip()
        return self.cad_loc.texto

    def _ativos_filtrados(self):
        termo = self.consulta_busca.texto.strip().casefold()
        if not termo:
            return list(self.ativos_brutos)
        return [
            ativo for ativo in self.ativos_brutos
            if termo in str(ativo.get('nome', '')).casefold()
            or termo in str(ativo.get('responsavel', '')).casefold()
            or termo in str(ativo.get('id', '')).casefold()
        ]

    def sincronizar_dados(self):
        db_inventario = ler_db()
        self.lista_ativos_display = []
        self.lista_vulns_ativas = []
        self.ativos_brutos = []
        self.alerta_ativo = False
        self.cor_alerta_atual = COR_VERDE_MATRIX
        
        pesos_severidade = {'baixa': 1, 'media': 2, 'alta': 3, 'critica': 4}
        max_peso = 0
        
        for dados in db_inventario.values():
            self.ativos_brutos.append(dados)
            vulns = dados.get('vulnerabilidades', [])
            
            vulns_em_aberto = [v for v in vulns if Equipamento.vulnerabilidade_esta_aberta(v)]
            status_txt = "ONLINE/SEGURO"
            
            if vulns_em_aberto:
                status_txt = f"ALERTA ({vulns_em_aberto[0].get('cve', 'N/A')})"
                self.alerta_ativo = True
                
                for v in vulns_em_aberto:
                    sev = v.get('severidade', 'baixa').lower()
                    peso_atual = pesos_severidade.get(sev, 1)
                    if peso_atual > max_peso:
                        max_peso = peso_atual
                        
                    self.lista_vulns_ativas.append({
                        "id_ativo": dados['id'],
                        "nome": dados.get('nome', ''),
                        "cve": v.get('cve', 'N/A'),
                        "descricao": v.get('descricao', ''),
                        "categoria": v.get('categoria', ''),
                        "severidade": v.get('severidade', ''),
                        "status": v.get('status', 'aberta')
                    })
            
            linha = f"ID: {dados['id']} | HOST: {dados.get('nome',''):<10} | STATUS: {status_txt}"
            self.lista_ativos_display.append(linha)

        self._atualizar_opcoes_salas()
        ativos_filtrados = self._ativos_filtrados()
        id_selecionado = (
            str(self.ativo_consulta_selecionado.get('id', ''))
            if self.ativo_consulta_selecionado else ""
        )
        self.ativo_consulta_selecionado = next(
            (ativo for ativo in ativos_filtrados if str(ativo.get('id', '')) == id_selecionado),
            ativos_filtrados[0] if ativos_filtrados else None
        )
            
        if max_peso == 1:
            self.cor_alerta_atual = COR_AMBAR 
            self.nivel_alerta_str = "ALERTA BAIXO"
        elif max_peso == 2:
            self.cor_alerta_atual = COR_LARANJA 
            self.nivel_alerta_str = "ALERTA MÉDIO"
        elif max_peso == 3:
            self.cor_alerta_atual = COR_VERMELHO_CLARO 
            self.nivel_alerta_str = "ALERTA ALTO"
        elif max_peso >= 4:
            self.cor_alerta_atual = COR_VERMELHO_ESCURO 
            self.nivel_alerta_str = "ALERTA CRÍTICO!"
        else:
            self.cor_alerta_atual = COR_VERDE_MATRIX
            self.nivel_alerta_str = "WORKSTATION SEGURA"
            
        # Proteção embutida: Se o servidor atual for deletado, tira o foco sem quebrar
        servidores_ids = [str(a['id']) for a in self.ativos_brutos if a.get('tipo', '').upper() == 'SERVIDOR']
        if getattr(self, 'servidor_foco_painel', None) not in servidores_ids:
            self.servidor_foco_painel = servidores_ids[0] if servidores_ids else None
            
        try:
            self.relatorio_risco = calcular_relatorio_risco_por_sala()
        except Exception as e:
            self.relatorio_risco = [
                "[ERRO CRÍTICO] Falha ao calcular a Matriz de Risco.",
                "Motivo: Possível banco de dados vazio ou sem dependências.",
                f"Detalhe Técnico: {str(e)}"
            ]

    # ==========================================
    # SUB-SESSÃO: PROCESSAMENTO DE EVENTOS
    # ==========================================
    def tratar_clique(self, pos_mouse):
        if self.modal_ativo:
            rect_modal = pygame.Rect(250, 60, LARGURA_TELA - 500, ALTURA_TELA - 120)
            rect_fechar = pygame.Rect(rect_modal.right - 48, rect_modal.y + 16, 32, 32)
            
            if rect_fechar.collidepoint(pos_mouse):
                self.modal_ativo = None
                self.mensagem_status = "" 
                return

            if self.modal_ativo == "NOTEBOOK_CRUD":
                if pygame.Rect(320, 130, 110, 34).collidepoint(pos_mouse): 
                    self.aba_crud_ativa = "LISTAR"
                    self.mensagem_status = ""
                elif pygame.Rect(440, 130, 110, 34).collidepoint(pos_mouse): 
                    self.aba_crud_ativa = "CADASTRAR"
                    self.mensagem_status = ""
                elif pygame.Rect(560, 130, 110, 34).collidepoint(pos_mouse): 
                    self.aba_crud_ativa = "ATUALIZAR"
                    self.mensagem_status = ""
                elif pygame.Rect(680, 130, 110, 34).collidepoint(pos_mouse): 
                    self.aba_crud_ativa = "REMOVER"
                    self.mensagem_status = ""

                if self.aba_crud_ativa == "LISTAR":
                    for r_item, dados in self.rects_ativos_crud:
                        if r_item.collidepoint(pos_mouse):
                            self.ativo_consulta_selecionado = dados
                            return

                if self.aba_crud_ativa in ["ATUALIZAR", "REMOVER"]:
                    for r_item, d in self.rects_ativos_crud:
                        if r_item.collidepoint(pos_mouse):
                            if self.aba_crud_ativa == "ATUALIZAR":
                                self.upd_id.texto = str(d['id'])
                                self.upd_resp.texto = ""
                                self.upd_loc.texto = ""
                            elif self.aba_crud_ativa == "REMOVER":
                                self.rem_id.texto = str(d['id'])
                            self.definir_mensagem(f"ALVO SELECIONADO: {d['nome']}. Dispare a ação.", COR_AMBAR)
                            return

                if self.aba_crud_ativa != "LISTAR" and pygame.Rect(320, 520, 340, 44).collidepoint(pos_mouse):
                    if self.aba_crud_ativa == "CADASTRAR":
                        resp_limpo = self.cad_resp.texto.strip()
                        loc_limpo = self._localidade_cadastro()
                        patrimonio = self.cad_host.texto.strip()
                        tipo_ativo = self.cad_tipo.texto

                        if not patrimonio.isdigit() or len(patrimonio) < 4:
                            self.definir_mensagem("O patrimônio deve ter pelo menos 4 dígitos.", COR_VERMELHO_NEON)
                            return
                        patrimonio_normalizado = str(int(patrimonio))
                        if any(str(ativo.get('id', '')) == patrimonio_normalizado for ativo in self.ativos_brutos):
                            self.definir_mensagem(f"Patrimônio {patrimonio} já cadastrado. Informe outro.", COR_VERMELHO_NEON)
                            return
                        if any(char.isdigit() for char in resp_limpo):
                            self.definir_mensagem("ERRO VALIDAÇÃO: O responsável não pode ter números.", COR_VERMELHO_NEON)
                            return
                        local_sem_formatacao = loc_limpo.replace(" ", "").replace("-", "")
                        if not local_sem_formatacao.isalnum():
                            self.definir_mensagem("ERRO VALIDAÇÃO: A localidade aceita letras, números, espaços e hífens.", COR_VERMELHO_NEON)
                            return

                        prefixo = self.prefixos_hostname[tipo_ativo]
                        hostname = f"{prefixo}{patrimonio}"
                        if any(str(ativo.get('nome', '')).casefold() == hostname.casefold() for ativo in self.ativos_brutos):
                            self.definir_mensagem(f"Hostname {hostname} já cadastrado. Informe outro patrimônio.", COR_VERMELHO_NEON)
                            return

                        dado_extra = self.cad_extra.texto.strip()
                        if tipo_ativo in ("NOTEBOOK", "DESKTOP") and (not dado_extra.isdigit() or int(dado_extra) < 1):
                            self.definir_mensagem("Informe a memória RAM em GB usando um inteiro positivo.", COR_VERMELHO_NEON)
                            return
                        if tipo_ativo == "SERVIDOR" and not dado_extra:
                            self.definir_mensagem("Informe o sistema operacional do servidor.", COR_VERMELHO_NEON)
                            return
                        if tipo_ativo == "ROTEADOR" and dado_extra.casefold() not in ("s", "sim", "atualizado", "yes", "y", "n", "não", "nao", "desatualizado", "no"):
                            self.definir_mensagem("Informe S ou N para o estado do firmware.", COR_VERMELHO_NEON)
                            return

                        sucesso = cadastrar_ativo(
                            patrimonio,
                            hostname,
                            self.cad_resp.texto,
                            loc_limpo,
                            tipo_ativo,
                            self.cad_extra.texto
                        )
                        if sucesso:
                            self.adicionar_log("CADASTRO", hostname.upper(), f"Ativo do tipo {tipo_ativo} inserido no inventário.")
                            self.cad_host.texto = ""
                            self.cad_resp.texto = ""
                            self.cad_extra.texto = ""
                            self.cad_sala_nova.texto = ""
                            self.cad_tipo.definir_valor("NOTEBOOK")
                            self.cad_host.prefixo = self.prefixos_hostname["NOTEBOOK"]
                            self._atualizar_rotulo_dado_extra()
                            self.definir_mensagem(f"SUCESSO: Ativo ({tipo_ativo}) cadastrado!", COR_VERDE_MATRIX)
                        else:
                            self.definir_mensagem("Cadastro não concluído. Confira os dados informados.", COR_VERMELHO_NEON)
                        self.sincronizar_dados()
                        if sucesso:
                            self.cad_loc.definir_valor(loc_limpo)
                        
                    elif self.aba_crud_ativa == "ATUALIZAR":
                        resp_limpo = self.upd_resp.texto.strip()
                        loc_limpo = self.upd_loc.texto.strip()
                        
                        if resp_limpo and any(char.isdigit() for char in resp_limpo):
                            self.definir_mensagem("ERRO VALIDAÇÃO: O responsável não pode ter números.", COR_VERMELHO_NEON)
                            return
                        if loc_limpo and any(char.isdigit() for char in loc_limpo):
                            self.definir_mensagem("ERRO VALIDAÇÃO: A localidade não pode conter números.", COR_VERMELHO_NEON)
                            return

                        # Traduz Hostname para ID evitando quebrar silenciosamente
                        alvo = self.upd_id.texto.strip().lower()
                        id_resolvido = alvo
                        for d in self.ativos_brutos:
                            if str(d.get('id', '')).lower() == alvo or d.get('nome', '').lower() == alvo:
                                id_resolvido = str(d.get('id', ''))
                                break
                        
                        sucesso = atualizar_ativo(id_resolvido, self.upd_resp.texto, self.upd_loc.texto)
                        if sucesso:
                            self.adicionar_log("ATUALIZAR", id_resolvido, "Propriedades modificadas.")
                            for c in self.campos_upd: c.texto = ""
                            self.definir_mensagem("SUCESSO: Dados do ativo atualizados!", COR_VERDE_MATRIX)
                        else:
                            self.definir_mensagem("ERRO: ID/Hostname não encontrado ou entrada inválida.", COR_VERMELHO_NEON)
                        self.sincronizar_dados()
                        
                    elif self.aba_crud_ativa == "REMOVER":
                        # Traduz Hostname para ID
                        alvo = self.rem_id.texto.strip().lower()
                        id_resolvido = alvo
                        for d in self.ativos_brutos:
                            if str(d.get('id', '')).lower() == alvo or d.get('nome', '').lower() == alvo:
                                id_resolvido = str(d.get('id', ''))
                                break
                                
                        sucesso = remover_ativo(id_resolvido)
                        if sucesso:
                            self.adicionar_log("REMOVER", id_resolvido, "Ativo deletado permanentemente da base de dados.")
                            for c in self.campos_rem: c.texto = ""
                            self.definir_mensagem("ALERTA: Ativo deletado permanentemente!", COR_AMBAR)
                        else:
                            self.definir_mensagem("ERRO: ID/Hostname não encontrado no sistema.", COR_VERMELHO_NEON)
                        self.sincronizar_dados()

            elif self.modal_ativo == "DASHBOARD_TELAO":
                for r_log, log_data in self.rects_logs:
                    if r_log.collidepoint(pos_mouse):
                        self.log_selecionado = log_data
                        return

            elif self.modal_ativo == "SERVIDOR_INFRA":
                for r_node, ativo in self.rects_matriz_risco:
                    if r_node.collidepoint(pos_mouse):
                        nome_busca = ativo.get('nome', '').lower()
                        risco_msg = "Risco Próprio: N/A | Risco Efetivo: N/A"
                        for linha in self.relatorio_risco:
                            if f"[{nome_busca}" in linha.lower():
                                risco_msg = linha.split("]")[-1].strip()
                                break
                        self.definir_mensagem(f"ANÁLISE DO NÓ [{ativo.get('nome', '').upper()}]: {risco_msg}", COR_AMBAR)
                        return

            elif self.modal_ativo == "VULN_PATCH":
                # Clique na lista de ATIVOS para preencher ID
                for r_item, d in self.rects_ativos_vuln:
                    if r_item.collidepoint(pos_mouse):
                        self.vuln_id.texto = str(d['id'])
                        self._limpar_busca_nvd()
                        self.preencher_vulnerabilidade_predefinida("")
                        self.vuln_log.texto = ""
                        self.definir_mensagem(f"ALVO: {d['nome']}. Preencha os dados e registre a falha.", COR_AMBAR)
                        return

                # Clique na lista de VULNERABILIDADES para corrigir
                for r_item, v in self.rects_vulns:
                    if r_item.collidepoint(pos_mouse):
                        self.vuln_id.texto = str(v['id_ativo'])
                        vulnerabilidade_predefinida = next(
                            (
                                item for item in CATALOGO_VULNERABILIDADES
                                if item['cve'].upper() == str(v['cve']).upper()
                                and item['descricao'].casefold() == str(v['descricao']).casefold()
                            ),
                            None
                        )
                        self.vuln_modelo.definir_valor(vulnerabilidade_predefinida['id'] if vulnerabilidade_predefinida else "")
                        self.vuln_cve.texto = v['cve']
                        self.vuln_desc.texto = v['descricao']
                        self.vuln_cat.texto = v['categoria']
                        self.vuln_sev.definir_valor(v['severidade'].lower())
                        self.vuln_stat.definir_valor(Equipamento.normalizar_status_vulnerabilidade(v['status']))
                        self.vuln_log.texto = ""
                        self.definir_mensagem(f"SELECIONADO: {v['nome']}. Descreva no Log o que fará para corrigir.", COR_AMBAR)
                        return

                # Sincronizado com a posição de desenho
                rect_btn_registrar = pygame.Rect(280, 520, 200, 48)
                rect_btn_corrigir = pygame.Rect(500, 520, 200, 48)
                
                if rect_btn_registrar.collidepoint(pos_mouse):
                    if not self.vuln_modelo.texto:
                        self.definir_mensagem("Selecione uma vulnerabilidade do catálogo.", COR_LARANJA)
                        return

                    # Traduz Hostname para ID
                    alvo = self.vuln_id.texto.strip().lower()
                    id_resolvido = alvo
                    for d in self.ativos_brutos:
                        if str(d.get('id', '')).lower() == alvo or d.get('nome', '').lower() == alvo:
                            id_resolvido = str(d.get('id', ''))
                            break

                    ativo_alvo = next(
                        (d for d in self.ativos_brutos if str(d.get('id', '')) == id_resolvido),
                        None
                    )
                    if ativo_alvo and str(ativo_alvo.get('tipo', '')).upper() == "SERVIDOR":
                        self.vuln_sev.definir_valor("critica")

                    sucesso = registrar_vulnerabilidade(id_resolvido, self.vuln_cve.texto, self.vuln_desc.texto, self.vuln_cat.texto, self.vuln_sev.texto, self.vuln_stat.texto)
                    if sucesso:
                        self.adicionar_log("INCIDENTE", id_resolvido, f"Nova falha reportada. CVE: {self.vuln_cve.texto}")
                        for c in self.campos_vuln: c.texto = ""
                        self._limpar_busca_nvd()
                        self.vuln_sev.definir_valor("")
                        self.vuln_stat.definir_valor(Equipamento.STATUS_ABERTO)
                        self.definir_mensagem("PERIGO: Vulnerabilidade de rede registrada!", COR_VERMELHO_NEON)
                    else:
                        self.definir_mensagem("ERRO: Verifique as regras/tuplas ou se o ID existe.", COR_VERMELHO_NEON)
                    self.sincronizar_dados()
                    
                elif rect_btn_corrigir.collidepoint(pos_mouse):
                    log_texto = self.vuln_log.texto.strip()
                    if not log_texto:
                        self.definir_mensagem("AÇÃO BLOQUEADA: É obrigatório detalhar no 'Log' o que foi feito.", COR_LARANJA)
                        return
                    if not self.vuln_id.texto.strip():
                        self.definir_mensagem("AÇÃO BLOQUEADA: Nenhum incidente selecionado.", COR_LARANJA)
                        return

                    alvo = self.vuln_id.texto.strip().lower()
                    id_resolvido = alvo
                    for d in self.ativos_brutos:
                        if str(d.get('id', '')).lower() == alvo or d.get('nome', '').lower() == alvo:
                            id_resolvido = str(d.get('id', ''))
                            break
                            
                    sucesso = corrigir_vulnerabilidade(id_resolvido, self.vuln_cve.texto, self.vuln_desc.texto)
                    if sucesso:
                        self.adicionar_log("CORREÇÃO", id_resolvido, log_texto)
                        for c in self.campos_vuln: c.texto = ""
                        self._limpar_busca_nvd()
                        self.vuln_sev.definir_valor("")
                        self.vuln_stat.definir_valor(Equipamento.STATUS_ABERTO)
                        self.definir_mensagem(f"SUCESSO! Ativo Seguro. Log salvo.", COR_VERDE_MATRIX)
                    else:
                        self.definir_mensagem("ERRO: Ativo não encontrado ou CVE não cadastrado.", COR_VERMELHO_NEON)
                    self.sincronizar_dados()

            if not pygame.Rect(250, 60, LARGURA_TELA - 500, ALTURA_TELA - 120).collidepoint(pos_mouse):
                self.modal_ativo = None
                self.mensagem_status = ""
            return

        if self.rect_notebook.collidepoint(pos_mouse): 
            self.modal_ativo = "NOTEBOOK_CRUD"
            self.mensagem_status = ""
        elif self.rect_servidor.collidepoint(pos_mouse): 
            self.modal_ativo = "SERVIDOR_INFRA"
            self.mensagem_status = ""
        elif self.rect_workstation.collidepoint(pos_mouse): 
            self.modal_ativo = "VULN_PATCH"
            self.mensagem_status = ""
        elif self.rect_telao.collidepoint(pos_mouse): 
            self.modal_ativo = "DASHBOARD_TELAO"
            self.mensagem_status = ""

    def processar_eventos(self):
        pos_mouse = pygame.mouse.get_pos()
        self.objeto_em_hover = None

        if not self.modal_ativo:
            if self.rect_notebook.collidepoint(pos_mouse): self.objeto_em_hover = "NOTEBOOK"
            elif self.rect_servidor.collidepoint(pos_mouse): self.objeto_em_hover = "SERVIDOR"
            elif self.rect_workstation.collidepoint(pos_mouse): self.objeto_em_hover = "WORKSTATION"
            elif self.rect_telao.collidepoint(pos_mouse): self.objeto_em_hover = "TELAO"

        campos_ativos = []
        if self.modal_ativo == "NOTEBOOK_CRUD":
            if self.aba_crud_ativa == "CADASTRAR": campos_ativos = self._campos_cadastro_ativos()
            elif self.aba_crud_ativa == "ATUALIZAR": campos_ativos = self.campos_upd
            elif self.aba_crud_ativa == "REMOVER": campos_ativos = self.campos_rem
            elif self.aba_crud_ativa == "LISTAR": campos_ativos = [self.consulta_busca]
        elif self.modal_ativo == "VULN_PATCH":
            campos_ativos = self.campos_vuln

        self._processar_busca_nvd()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: self.rodando = False
            
            if evento.type == pygame.MOUSEWHEEL:
                if self.modal_ativo == "DASHBOARD_TELAO":
                    self.scroll_logs -= evento.y
                    max_scroll = max(0, len(self.historico_logs) - 12)
                    self.scroll_logs = max(0, min(self.scroll_logs, max_scroll))
                
                elif self.modal_ativo == "NOTEBOOK_CRUD" and self.aba_crud_ativa in ["ATUALIZAR", "REMOVER"]:
                    painel_ativos = pygame.Rect(630, 190, 360, 200)
                    if painel_ativos.collidepoint(pos_mouse):
                        self.scroll_crud_ativos -= evento.y
                        max_scroll = max(0, len(self.ativos_brutos) - 7)
                        self.scroll_crud_ativos = max(0, min(self.scroll_crud_ativos, max_scroll))

                elif self.modal_ativo == "NOTEBOOK_CRUD" and self.aba_crud_ativa == "LISTAR":
                    painel_resultados = pygame.Rect(290, 220, 340, 230)
                    if painel_resultados.collidepoint(pos_mouse):
                        self.scroll_resultados_consulta -= evento.y
                        max_scroll = max(0, len(self._ativos_filtrados()) - 7)
                        self.scroll_resultados_consulta = max(0, min(self.scroll_resultados_consulta, max_scroll))
                        
                elif self.modal_ativo == "VULN_PATCH":
                    painel_ativos = pygame.Rect(600, 140, 400, 135)
                    painel_vulns = pygame.Rect(600, 290, 400, 135)
                    if painel_ativos.collidepoint(pos_mouse):
                        self.scroll_vuln_inv -= evento.y
                        max_scroll = max(0, len(self.ativos_brutos) - 4)
                        self.scroll_vuln_inv = max(0, min(self.scroll_vuln_inv, max_scroll))
                    elif painel_vulns.collidepoint(pos_mouse):
                        self.scroll_vuln_lista -= evento.y
                        max_scroll = max(0, len(self.lista_vulns_ativas) - 4)
                        self.scroll_vuln_lista = max(0, min(self.scroll_vuln_lista, max_scroll))

                elif self.modal_ativo == "SERVIDOR_INFRA":
                    area_gavetas = pygame.Rect(270, 130, 200, 460)
                    if area_gavetas.collidepoint(pos_mouse):
                        self.scroll_gaveta_servidores -= evento.y
                        max_scroll = max(0, len([a for a in self.ativos_brutos if a.get('tipo', '').upper() == 'SERVIDOR']) - 9)
                        self.scroll_gaveta_servidores = max(0, min(self.scroll_gaveta_servidores, max_scroll))

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_TAB:
                for i, c in enumerate(campos_ativos):
                    if c.ativo:
                        c.ativo = False
                        c.cor = c.cor_inativa
                        next_i = (i + 1) % len(campos_ativos)
                        campos_ativos[next_i].ativo = True
                        campos_ativos[next_i].cor = campos_ativos[next_i].cor_ativa
                        break
                else:
                    if campos_ativos: 
                        campos_ativos[0].ativo = True
                        campos_ativos[0].cor = campos_ativos[0].cor_ativa

            for campo in campos_ativos:
                texto_anterior = campo.texto
                filtro_anterior = campo.filtro if campo is self.vuln_modelo else None
                campo.processar_evento(evento)
                if campo is self.cad_tipo and campo.texto != texto_anterior:
                    self.cad_host.prefixo = self.prefixos_hostname[campo.texto]
                    self._atualizar_rotulo_dado_extra()
                if campo is self.cad_loc and campo.texto == "__NOVA_SALA__" and campo.texto != texto_anterior:
                    self.cad_sala_nova.texto = ""
                    self.cad_sala_nova.ativo = True
                    self.cad_sala_nova.cor = self.cad_sala_nova.cor_ativa
                if campo is self.consulta_busca and campo.texto != texto_anterior:
                    filtrados = self._ativos_filtrados()
                    self.scroll_resultados_consulta = 0
                    self.ativo_consulta_selecionado = filtrados[0] if filtrados else None
                if campo is self.vuln_modelo:
                    if campo.texto != texto_anterior:
                        if campo.texto == "__NVD_MORE__":
                            campo.definir_valor("")
                            self._programar_proxima_pagina_nvd()
                        else:
                            self.preencher_vulnerabilidade_predefinida(campo.texto)
                    if campo.filtro != filtro_anterior:
                        self.preencher_vulnerabilidade_predefinida("")
                        self._programar_busca_nvd(campo.filtro)
                if (
                    campo in (self.cad_tipo, self.cad_loc)
                    and evento.type == pygame.MOUSEBUTTONDOWN
                    and campo.texto != texto_anterior
                ):
                    break

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                self.tratar_clique(pos_mouse)

    # ==========================================
    # SUB-SESSÃO: RENDERIZAÇÃO GRÁFICA
    # ==========================================
    def desenhar_cenario(self):
        self.tela.fill(COR_FUNDO)
        pygame.draw.rect(self.tela, COR_PAREDE, (0, 0, LARGURA_TELA, 340))
        
        for drop in self.bg_drops:
            drop['y'] += drop['speed']
            if drop['y'] > 340: 
                drop['y'] = random.randint(-200, -10)
                drop['x'] = random.randint(0, LARGURA_TELA)
                drop['char'] = random.choice(['0', '1', 'A', 'B', 'C', 'D', 'E', 'F', 'X'])
            txt_superficie = self.fonte_p.render(drop['char'], True, (0, 35, 0)) 
            self.tela.blit(txt_superficie, (drop['x'], drop['y']))
            
        pygame.draw.line(self.tela, (30, 45, 70), (0, 340), (LARGURA_TELA, 340), 2)
        pygame.draw.rect(self.tela, COR_CHAO, (0, 340, LARGURA_TELA, ALTURA_TELA - 340))
        for y in range(370, ALTURA_TELA, 45): pygame.draw.line(self.tela, COR_GRADE, (0, y), (LARGURA_TELA, y), 1)
        for x in range(-200, LARGURA_TELA + 300, 120): pygame.draw.line(self.tela, COR_GRADE, (x, ALTURA_TELA), (LARGURA_TELA // 2, 280), 1)
        pygame.draw.rect(self.tela, (20, 30, 48), (420, 520, 320, 130))
        pygame.draw.rect(self.tela, (38, 56, 88), (420, 520, 320, 130), 2)
        pygame.draw.line(self.tela, COR_CIANO_NEON, (430, 530), (730, 530), 2)
        pygame.draw.rect(self.tela, (18, 26, 42), (110, 480, 250, 160))
        pygame.draw.rect(self.tela, (34, 50, 78), (110, 480, 250, 160), 2)

    def desenhar_objetos(self):
        fase_telao = 0
        area_rolagem = pygame.Rect(0, 0, 0, 0)
        
        cor_nb = COR_CIANO_NEON if self.objeto_em_hover == "NOTEBOOK" else (50, 80, 120)
        rect_tela_note = pygame.Rect(self.rect_notebook.x + 20, self.rect_notebook.y, 140, 65)
        pygame.draw.rect(self.tela, (15, 20, 30), rect_tela_note)
        pygame.draw.rect(self.tela, cor_nb, rect_tela_note, 2)
        pygame.draw.line(self.tela, COR_VERDE_MATRIX, (rect_tela_note.x + 10, rect_tela_note.y + 18), (rect_tela_note.x + 85, rect_tela_note.y + 18), 2)
        pygame.draw.line(self.tela, COR_CIANO_NEON, (rect_tela_note.x + 10, rect_tela_note.y + 32), (rect_tela_note.x + 110, rect_tela_note.y + 32), 2)
        pygame.draw.rect(self.tela, (30, 42, 60), (self.rect_notebook.x, self.rect_notebook.y + 65, 180, 25))
        pygame.draw.rect(self.tela, cor_nb, (self.rect_notebook.x, self.rect_notebook.y + 65, 180, 25), 2)
        self.tela.blit(self.fonte_p.render("[ NOTEBOOK: CRUD ATIVOS ]", True, COR_CIANO_NEON), (self.rect_notebook.x - 5, self.rect_notebook.y - 20))

        cor_srv = COR_AMBAR if self.objeto_em_hover == "SERVIDOR" else (40, 60, 90)
        pygame.draw.rect(self.tela, (14, 20, 32), self.rect_servidor)
        pygame.draw.rect(self.tela, cor_srv, self.rect_servidor, 2)
        ticks = pygame.time.get_ticks()
        for i in range(7):
            r_blade = pygame.Rect(self.rect_servidor.x + 15, self.rect_servidor.y + 30 + (i * 60), 170, 48)
            pygame.draw.rect(self.tela, (22, 32, 50), r_blade)
            pygame.draw.rect(self.tela, (40, 58, 86), r_blade, 1)
            self.tela.blit(self.fonte_p.render(f"U0{i+1}", True, COR_TEXTO_MUTED), (r_blade.x + 8, r_blade.y + 8))
            led_aceso = ((ticks // (280 + i * 85)) % 2 == 0)
            
            if self.alerta_ativo:
                cor_led = self.cor_alerta_atual if led_aceso else (80, 10, 20)
            else:
                cor_led = COR_VERDE_MATRIX if led_aceso else COR_AMBAR
                
            pygame.draw.circle(self.tela, cor_led, (r_blade.x + 150, r_blade.y + 18), 4)
            
        self.tela.blit(self.fonte_p.render("[ SERVIDOR: JSON / RISCO ]", True, COR_AMBAR), (self.rect_servidor.x, self.rect_servidor.y - 22))

        piscar = self.alerta_ativo and ((ticks // 250) % 2 == 0)
        cor_pc = self.cor_alerta_atual if piscar else (COR_CIANO_NEON if self.objeto_em_hover == "WORKSTATION" else (45, 65, 95))
        fundo_tela = (80, 10, 20) if piscar else ((15, 30, 45) if self.objeto_em_hover == "WORKSTATION" else (15, 22, 35))
        rect_pc_tela = pygame.Rect(self.rect_workstation.x + 20, self.rect_workstation.y, 150, 105)
        pygame.draw.rect(self.tela, fundo_tela, rect_pc_tela)
        pygame.draw.rect(self.tela, cor_pc, rect_pc_tela, 3 if self.alerta_ativo else 2)
        pygame.draw.rect(self.tela, (30, 45, 65), (self.rect_workstation.x + 85, self.rect_workstation.y + 105, 20, 25))
        pygame.draw.rect(self.tela, (30, 45, 65), (self.rect_workstation.x + 65, self.rect_workstation.y + 125, 60, 10))
        
        rotulo_pc = self.nivel_alerta_str if self.alerta_ativo else "WORKSTATION SEGURA"
        self.tela.blit(self.fonte_p.render(f"[ {rotulo_pc} ]", True, self.cor_alerta_atual if self.alerta_ativo else COR_VERDE_MATRIX), (self.rect_workstation.x, self.rect_workstation.y - 20))

        # =======================================================
        # 1. ALERTA DA WORKSTATION (EMOJI Bug)
        # =======================================================
        if self.alerta_ativo:
            bug_x = self.rect_workstation.x + 75
            bug_y = self.rect_workstation.y - 65 + int(math.sin(ticks / 140.0) * 8)
            
            pygame.draw.rect(self.tela, (40, 8, 16), (bug_x - 14, bug_y - 4, 46, 38))
            pygame.draw.rect(self.tela, self.cor_alerta_atual, (bug_x - 14, bug_y - 4, 46, 38), 2)
            
            try: 
                self.tela.blit(self.fonte_emoji.render("👾", True, (255, 255, 255)), (bug_x - 6, bug_y - 2))
            except Exception: 
                self.tela.blit(self.fonte_g.render("!", True, self.cor_alerta_atual), (bug_x + 2, bug_y))

        # =======================================================
        # 2. DASHBOARD / TELÃO
        # =======================================================
        pygame.draw.rect(self.tela, (12, 18, 28), self.rect_telao)
        pygame.draw.rect(self.tela, COR_CIANO_NEON if self.objeto_em_hover == "TELAO" else (30, 48, 75), self.rect_telao, 2)
        
        fase_telao = (ticks // 10000) % 2 
        titulo_telao = "DASHBOARD : LOGS EM TEMPO REAL" if fase_telao == 0 else "DASHBOARD [AMEAÇAS]: VULNERABILIDADES ATIVAS"
        cor_titulo_telao = COR_CIANO_NEON if fase_telao == 0 else COR_VERMELHO_NEON
        self.tela.blit(self.fonte_m.render(titulo_telao, True, cor_titulo_telao), (self.rect_telao.x + 16, self.rect_telao.y + 10))
        
        area_rolagem = pygame.Rect(self.rect_telao.x + 10, self.rect_telao.y + 35, self.rect_telao.width - 20, self.rect_telao.height - 45)
        self.tela.set_clip(area_rolagem)
        
        if fase_telao == 0:
            logs_para_mostrar = self.historico_logs[:25]
            if len(logs_para_mostrar) >= 8:
                deslocamento_y = (ticks / 30.0) % (len(logs_para_mostrar) * 30)
            else:
                deslocamento_y = 0
                
            pos_y_atual = area_rolagem.y - deslocamento_y + 20
            
            for _ in range(2 if deslocamento_y > 0 else 1):
                for log in logs_para_mostrar:
                    cor_log = COR_VERDE_MATRIX if log['acao'] == "CORREÇÃO" else COR_VERMELHO_NEON if log['acao'] == "INCIDENTE" else COR_AMBAR
                    txt_log = f"> [{log['hora']}] {log['acao']}: {log['alvo']} - {log['detalhes'][:30]}..."
                    self.tela.blit(self.fonte_p.render(txt_log, True, cor_log), (area_rolagem.x + 5, pos_y_atual))
                    pos_y_atual += 30
                    
        else:
            if not self.lista_vulns_ativas:
                self.tela.blit(self.fonte_p.render("> SISTEMA 100% SEGURO. Nenhuma ameaça ativa.", True, COR_VERDE_MATRIX), (area_rolagem.x + 5, area_rolagem.y + 20))
            else:
                if len(self.lista_vulns_ativas) >= 8:
                    deslocamento_y = (ticks / 30.0) % (len(self.lista_vulns_ativas) * 30)
                else:
                    deslocamento_y = 0
                    
                pos_y_atual = area_rolagem.y - deslocamento_y + 20
                
                for _ in range(2 if deslocamento_y > 0 else 1):
                    for v in self.lista_vulns_ativas:
                        txt_vuln = f"> URGENTE! Ativo ID:{v['id_ativo']} ({v['nome']}) - CVE: {v['cve']} [{v['severidade'].upper()}]"
                        
                        # CORREÇÃO DE COR DINÂMICA
                        sev_log = v['severidade'].lower()
                        if sev_log == 'baixa': cor_log_v = COR_AMBAR
                        elif sev_log == 'media': cor_log_v = COR_LARANJA
                        elif sev_log == 'alta': cor_log_v = COR_VERMELHO_CLARO
                        else: cor_log_v = COR_VERMELHO_ESCURO
                        
                        self.tela.blit(self.fonte_p.render(txt_vuln, True, cor_log_v), (area_rolagem.x + 5, pos_y_atual))
                        pos_y_atual += 30
            
        self.tela.set_clip(None)

    def desenhar_modais(self):
        if not self.modal_ativo: return

        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((5, 8, 15, 210))
        self.tela.blit(overlay, (0, 0))

        rect_modal = pygame.Rect(250, 60, LARGURA_TELA - 500, ALTURA_TELA - 120)
        pygame.draw.rect(self.tela, COR_PAINEL, rect_modal)
        pygame.draw.rect(self.tela, COR_PAINEL_BORDA, rect_modal, 2)

        rect_x = pygame.Rect(rect_modal.right - 48, rect_modal.y + 16, 32, 32)
        pygame.draw.rect(self.tela, (40, 20, 25), rect_x)
        pygame.draw.rect(self.tela, COR_VERMELHO_NEON, rect_x, 1)
        self.tela.blit(self.fonte_m.render("X", True, COR_VERMELHO_NEON), (rect_x.x + 10, rect_x.y + 6))

        pos_mouse = pygame.mouse.get_pos()

        if self.modal_ativo == "NOTEBOOK_CRUD":
            self.tela.blit(self.fonte_g.render("GERENCIADOR DE ATIVOS", True, COR_CIANO_NEON), (rect_modal.x + 30, rect_modal.y + 24))
            
            abas = [("LISTAR", 320), ("CADASTRAR", 440), ("ATUALIZAR", 560), ("REMOVER", 680)]
            for nome, x in abas:
                r_aba = pygame.Rect(x, 125, 110, 34)
                ativa = (self.aba_crud_ativa == nome)
                pygame.draw.rect(self.tela, (28, 48, 76) if ativa else (18, 26, 38), r_aba)
                pygame.draw.rect(self.tela, COR_CIANO_NEON if ativa else (40, 58, 85), r_aba, 1)
                self.tela.blit(self.fonte_p.render(nome, True, COR_CIANO_NEON if ativa else COR_TEXTO_MUTED), (r_aba.x + 16, r_aba.y + 8))

            corpo = pygame.Rect(rect_modal.x + 30, 175, rect_modal.width - 60, 290)
            pygame.draw.rect(self.tela, (12, 18, 28), corpo)
            pygame.draw.rect(self.tela, (30, 45, 68), corpo, 1)

            if self.aba_crud_ativa == "LISTAR":
                self.consulta_busca.desenhar(self.tela)
                painel_resultados = pygame.Rect(290, 220, 340, 230)
                painel_detalhes = pygame.Rect(640, 220, 350, 230)
                pygame.draw.rect(self.tela, (8, 12, 18), painel_resultados)
                pygame.draw.rect(self.tela, (40, 58, 85), painel_resultados, 1)
                pygame.draw.rect(self.tela, (8, 12, 18), painel_detalhes)
                pygame.draw.rect(self.tela, COR_CIANO_NEON, painel_detalhes, 1)
                self.tela.blit(self.fonte_p.render("ATIVOS ENCONTRADOS", True, COR_CIANO_NEON), (painel_resultados.x + 10, painel_resultados.y + 8))
                self.tela.blit(self.fonte_m.render("DETALHES DO ATIVO", True, COR_CIANO_NEON), (painel_detalhes.x + 12, painel_detalhes.y + 8))

                self.rects_ativos_crud = []
                ativos_filtrados = self._ativos_filtrados()
                ativos_visiveis = ativos_filtrados[self.scroll_resultados_consulta:self.scroll_resultados_consulta + 7]
                if not ativos_filtrados:
                    self.tela.blit(self.fonte_p.render("Nenhum ativo correspondente.", True, COR_TEXTO_MUTED), (painel_resultados.x + 10, painel_resultados.y + 42))
                else:
                    for indice, ativo in enumerate(ativos_visiveis):
                        rect_ativo = pygame.Rect(painel_resultados.x + 8, painel_resultados.y + 34 + indice * 27, 324, 24)
                        selecionado = (
                            self.ativo_consulta_selecionado
                            and str(self.ativo_consulta_selecionado.get('id')) == str(ativo.get('id'))
                        )
                        pygame.draw.rect(self.tela, (30, 55, 72) if selecionado else (18, 24, 32), rect_ativo)
                        pygame.draw.rect(self.tela, COR_CIANO_NEON if selecionado else (40, 58, 85), rect_ativo, 1)
                        texto_ativo = f"{ativo.get('nome', '')} | {ativo.get('responsavel', '')}"
                        while texto_ativo and self.fonte_p.size(texto_ativo)[0] > rect_ativo.width - 12:
                            texto_ativo = texto_ativo[:-1]
                        self.tela.blit(self.fonte_p.render(texto_ativo, True, COR_TEXTO), (rect_ativo.x + 6, rect_ativo.y + 4))
                        self.rects_ativos_crud.append((rect_ativo, ativo))

                if self.ativo_consulta_selecionado:
                    ativo = self.ativo_consulta_selecionado
                    tipo = str(ativo.get('tipo', '')).upper()
                    tipo_exibicao = {
                        "NOTEBOOK": "Notebook",
                        "SERVIDOR": "Servidor",
                        "DESKTOP": "Desktop",
                        "ROTEADOR": "Roteador"
                    }.get(tipo, tipo or "Não informado")
                    detalhes = [
                        ("Hostname", ativo.get('nome', 'Não informado')),
                        ("Patrimônio", ativo.get('id', 'Não informado')),
                        ("Usuário", ativo.get('responsavel', 'Não informado')),
                        ("Local", ativo.get('local', 'Não informado')),
                        ("Tipo", tipo_exibicao)
                    ]
                    if 'qnt_ram' in ativo:
                        detalhes.append(("Memória", f"{ativo['qnt_ram']} GB RAM"))
                    if 'sistema_operacional' in ativo:
                        detalhes.append(("Sistema", ativo['sistema_operacional']))
                    if 'firmware_atualizado' in ativo:
                        firmware = "Atualizado" if ativo['firmware_atualizado'] else "Desatualizado"
                        detalhes.append(("Firmware", firmware))

                    self.tela.set_clip(pygame.Rect(painel_detalhes.x + 8, painel_detalhes.y + 34, painel_detalhes.width - 16, painel_detalhes.height - 42))
                    for indice, (rotulo, valor) in enumerate(detalhes):
                        texto_detalhe = f"{rotulo}: {valor}"
                        self.tela.blit(self.fonte_p.render(texto_detalhe, True, COR_TEXTO), (painel_detalhes.x + 12, painel_detalhes.y + 38 + indice * 25))
                    self.tela.set_clip(None)
                else:
                    self.tela.blit(self.fonte_p.render("Selecione um ativo para ver os dados.", True, COR_TEXTO_MUTED), (painel_detalhes.x + 12, painel_detalhes.y + 45))
            
            elif self.aba_crud_ativa == "CADASTRAR":
                for campo in self._campos_cadastro_ativos():
                    campo.desenhar(self.tela)
                self.cad_tipo.desenhar_menu(self.tela)
                if self.cad_loc.texto != "__NOVA_SALA__":
                    self.cad_loc.desenhar_menu(self.tela)
                    
                col_x = 630
                col_y = 190
                self.tela.blit(self.fonte_m.render("IDENTIFICAÇÃO DO ATIVO", True, COR_AMBAR), (col_x, col_y))
                self.tela.blit(self.fonte_p.render("Selecione o tipo; prefixo automático.", True, COR_CIANO_NEON), (col_x, col_y + 32))
                self.tela.blit(self.fonte_p.render("Use 4+ dígitos para o patrimônio.", True, COR_TEXTO_MUTED), (col_x, col_y + 54))
                self.tela.blit(self.fonte_p.render("RAM: número em GB | Servidor: SO", True, COR_TEXTO_MUTED), (col_x, col_y + 92))
                self.tela.blit(self.fonte_p.render("Roteador: firmware S/N", True, COR_TEXTO_MUTED), (col_x, col_y + 114))
                self.tela.blit(self.fonte_p.render("Local: Sala A-D ou + Nova sala", True, COR_TEXTO_MUTED), (col_x, col_y + 150))
                
            elif self.aba_crud_ativa in ["ATUALIZAR", "REMOVER"]:
                if self.aba_crud_ativa == "ATUALIZAR":
                    for campo in self.campos_upd: campo.desenhar(self.tela)
                else:
                    for campo in self.campos_rem: campo.desenhar(self.tela)
                
                painel_ativos = pygame.Rect(630, 190, 360, 200)
                pygame.draw.rect(self.tela, (12, 18, 28), painel_ativos)
                pygame.draw.rect(self.tela, (30, 45, 68), painel_ativos, 2)
                self.tela.blit(self.fonte_m.render("INVENTÁRIO (SCROLL P/ NAVEGAR)", True, COR_CIANO_NEON), (painel_ativos.x + 10, painel_ativos.y + 10))

                self.rects_ativos_crud = []
                ativos_visiveis = self.ativos_brutos[self.scroll_crud_ativos : self.scroll_crud_ativos + 7]
                
                for i, d in enumerate(ativos_visiveis):
                    r_item = pygame.Rect(painel_ativos.x + 10, painel_ativos.y + 35 + (i * 22), 340, 20)
                    pygame.draw.rect(self.tela, (25, 35, 50), r_item)
                    pygame.draw.rect(self.tela, (40, 58, 85), r_item, 1)
                    txt = f"ID: {d['id']} | {d.get('nome', '')} | {d.get('tipo', '')}"
                    self.tela.blit(self.fonte_p.render(txt, True, COR_TEXTO), (r_item.x + 10, r_item.y + 3))
                    self.rects_ativos_crud.append((r_item, d))

            if self.mensagem_status:
                self.tela.blit(self.fonte_m.render(self.mensagem_status, True, self.cor_status), (320, 490))

            if self.aba_crud_ativa != "LISTAR":
                btn_exec = pygame.Rect(320, 520, 340, 44)
                pygame.draw.rect(self.tela, (20, 45, 60), btn_exec)
                pygame.draw.rect(self.tela, COR_CIANO_NEON, btn_exec, 1)
                self.tela.blit(self.fonte_m.render(f"DISPARAR: {self.aba_crud_ativa}", True, COR_CIANO_NEON), (btn_exec.x + 20, btn_exec.y + 12))

        elif self.modal_ativo == "DASHBOARD_TELAO":
            self.tela.blit(self.fonte_g.render("DASHBOARD PRINCIPAL // AUDITORIA E LOGS", True, COR_CIANO_NEON), (rect_modal.x + 30, rect_modal.y + 24))
            
            corpo = pygame.Rect(rect_modal.x + 30, rect_modal.y + 70, rect_modal.width - 60, 390)
            pygame.draw.rect(self.tela, (12, 18, 28), corpo)
            pygame.draw.rect(self.tela, (30, 45, 68), corpo, 1)
            
            area_logs = pygame.Rect(corpo.x + 10, corpo.y + 10, 380, 370)
            pygame.draw.rect(self.tela, (8, 12, 18), area_logs)
            pygame.draw.rect(self.tela, (40, 58, 85), area_logs, 1)
            self.tela.blit(self.fonte_p.render("HISTÓRICO DE AUDITORIA (Scroll do Mouse):", True, COR_AMBAR), (area_logs.x + 10, area_logs.y + 10))

            self.rects_logs = []
            logs_visiveis = self.historico_logs[self.scroll_logs:self.scroll_logs + 12]
            for i, log in enumerate(logs_visiveis):
                r_log = pygame.Rect(area_logs.x + 10, area_logs.y + 35 + (i * 26), 360, 24)
                cor_fundo_log = (20, 35, 50) if self.log_selecionado == log else (15, 20, 30)
                pygame.draw.rect(self.tela, cor_fundo_log, r_log)
                pygame.draw.rect(self.tela, (30, 45, 60), r_log, 1)
                txt_log = f"[{log['hora']}] {log['acao']} - Alvo: {log['alvo']}"
                
                cor_log_txt = COR_TEXTO
                if log['acao'] == "CORREÇÃO": cor_log_txt = COR_VERDE_MATRIX
                elif log['acao'] == "INCIDENTE": cor_log_txt = COR_VERMELHO_NEON
                elif log['acao'] == "REMOVER": cor_log_txt = COR_AMBAR
                
                self.tela.blit(self.fonte_p.render(txt_log, True, cor_log_txt), (r_log.x + 8, r_log.y + 4))
                self.rects_logs.append((r_log, log))

            area_detalhe = pygame.Rect(corpo.x + 400, corpo.y + 10, 300, 370)
            pygame.draw.rect(self.tela, (10, 15, 22), area_detalhe)
            pygame.draw.rect(self.tela, COR_CIANO_NEON, area_detalhe, 1)
            self.tela.blit(self.fonte_m.render("INSPEÇÃO DE EVENTO", True, COR_CIANO_NEON), (area_detalhe.x + 10, area_detalhe.y + 10))
            
            if self.log_selecionado:
                self.tela.blit(self.fonte_p.render(f"Ação: {self.log_selecionado['acao']}", True, COR_TEXTO_MUTED), (area_detalhe.x + 10, area_detalhe.y + 40))
                self.tela.blit(self.fonte_p.render(f"Hora: {self.log_selecionado['hora']}", True, COR_TEXTO_MUTED), (area_detalhe.x + 10, area_detalhe.y + 60))
                self.tela.blit(self.fonte_p.render(f"Alvo: {self.log_selecionado['alvo']}", True, COR_TEXTO_MUTED), (area_detalhe.x + 10, area_detalhe.y + 80))
                
                palavras = self.log_selecionado['detalhes'].split(' ')
                linhas = []
                linha_atual = ""
                for p in palavras:
                    if len(linha_atual + p) < 30: linha_atual += p + " "
                    else:
                        linhas.append(linha_atual)
                        linha_atual = p + " "
                linhas.append(linha_atual)
                
                self.tela.blit(self.fonte_p.render("Comentário / Detalhe:", True, COR_AMBAR), (area_detalhe.x + 10, area_detalhe.y + 110))
                for idx, l in enumerate(linhas):
                    self.tela.blit(self.fonte_p.render(l, True, COR_TEXTO), (area_detalhe.x + 10, area_detalhe.y + 130 + (idx * 20)))
            else:
                self.tela.blit(self.fonte_p.render("Selecione um log para", True, (60, 80, 100)), (area_detalhe.x + 10, area_detalhe.y + 120))
                self.tela.blit(self.fonte_p.render("visualizar os dados.", True, (60, 80, 100)), (area_detalhe.x + 10, area_detalhe.y + 140))

        elif self.modal_ativo == "SERVIDOR_INFRA":
            linha_global = next(
                (linha for linha in self.relatorio_risco if linha.startswith("RISCO GLOBAL EFETIVO TOTAL:")),
                "RISCO GLOBAL EFETIVO TOTAL: N/A"
            )
            risco_global_total = linha_global.split(":", 1)[1].strip()
            servidor_focado = next(
                (servidor for servidor in self.ativos_brutos if str(servidor.get('id', '')) == str(self.servidor_foco_painel)),
                None
            )
            sala_focada = str(servidor_focado.get('local', '')).strip() if servidor_focado else ""
            titulo_risco = f"RISCO DA SALA {sala_focada or '—'} | GLOBAL: {risco_global_total}"
            self.tela.blit(self.fonte_g.render(titulo_risco, True, COR_AMBAR), (rect_modal.x + 30, rect_modal.y + 24))
            
            # 1. DIVIDIR A TELA EM DOIS PAINÉIS
            area_gavetas = pygame.Rect(rect_modal.x + 20, rect_modal.y + 70, 200, 460)
            area_arvore = pygame.Rect(rect_modal.x + 240, rect_modal.y + 70, rect_modal.width - 260, 460)
            
            pygame.draw.rect(self.tela, (12, 18, 28), area_gavetas)
            pygame.draw.rect(self.tela, (30, 45, 68), area_gavetas, 1)
            self.tela.blit(self.fonte_m.render("SERVIDORES", True, COR_CIANO_NEON), (area_gavetas.x + 10, area_gavetas.y + 10))

            pygame.draw.rect(self.tela, (10, 15, 20), area_arvore)
            pygame.draw.rect(self.tela, COR_AMBAR, area_arvore, 1)

            self.rects_matriz_risco = []

            def obter_risco_efetivo(nome_busca):
                for linha in self.relatorio_risco:
                    if f"[{nome_busca.lower()}" in linha.lower():
                        try: return linha.split("Risco Efetivo:")[-1].strip()
                        except: pass
                return "0.00"

            def desenhar_icone_ativo(x, y, ativo):
                tipo = ativo.get('tipo', '').upper()
                nome = ativo.get('nome', 'UNK').upper()
                risco_efetivo = obter_risco_efetivo(nome)
                
                vulns_abertas = [v for v in ativo.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]
                tem_alerta = len(vulns_abertas) > 0
                
                # CORREÇÃO: COR DE BORDA DINÂMICA NA ÁRVORE DE INFRA
                if tem_alerta:
                    pesos = {'baixa': 1, 'media': 2, 'alta': 3, 'critica': 4}
                    max_sev = max([pesos.get(v.get('severidade', 'baixa').lower(), 1) for v in vulns_abertas])
                    severidade_principal = next(
                        v.get('severidade', 'baixa').upper()
                        for v in vulns_abertas
                        if pesos.get(v.get('severidade', 'baixa').lower(), 1) == max_sev
                    )
                    
                    if max_sev == 1: cor_borda = COR_AMBAR
                    elif max_sev == 2: cor_borda = COR_LARANJA
                    elif max_sev == 3: cor_borda = COR_VERMELHO_CLARO
                    else: cor_borda = COR_VERMELHO_ESCURO
                    
                    cor_fundo = (40, 10, 10) 
                else:
                    cor_borda = COR_VERDE_MATRIX
                    cor_fundo = (15, 25, 35)
                
                rect_clique = pygame.Rect(x - 30, y - 50, 60, 100) if tipo == "SERVIDOR" else pygame.Rect(x - 40, y - 40, 80, 80)
                if rect_clique.collidepoint(pos_mouse):
                    cor_fundo = (80, 20, 20) if tem_alerta else (30, 45, 65)

                if tipo == "SERVIDOR":
                    rect_vis = pygame.Rect(x - 30, y - 50, 60, 100)
                    pygame.draw.rect(self.tela, cor_fundo, rect_vis, border_radius=6)
                    pygame.draw.rect(self.tela, cor_borda, rect_vis, 2, border_radius=6)
                    for j in range(3):
                        pygame.draw.line(self.tela, cor_borda, (x - 20, y - 20 + j*20), (x + 20, y - 20 + j*20), 2)
                        
                elif tipo == "DESKTOP":
                    monitor = pygame.Rect(x - 35, y - 25, 70, 40)
                    pygame.draw.rect(self.tela, cor_fundo, monitor, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, monitor, 2, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, (x - 8, y + 15, 16, 10)) 
                    pygame.draw.line(self.tela, cor_borda, (x - 20, y + 25), (x + 20, y + 25), 3) 
                    
                elif tipo == "NOTEBOOK":
                    tela_nb = pygame.Rect(x - 30, y - 20, 60, 35)
                    pygame.draw.rect(self.tela, cor_fundo, tela_nb, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, tela_nb, 2, border_radius=4)
                    base_nb = pygame.Rect(x - 35, y + 15, 70, 8)
                    pygame.draw.rect(self.tela, cor_fundo, base_nb, border_radius=2)
                    pygame.draw.rect(self.tela, cor_borda, base_nb, 2, border_radius=2)
                    
                elif tipo == "ROTEADOR":
                    rot_box = pygame.Rect(x - 35, y - 5, 70, 15)
                    pygame.draw.rect(self.tela, cor_fundo, rot_box, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, rot_box, 2, border_radius=4)
                    pygame.draw.line(self.tela, cor_borda, (x - 20, y - 5), (x - 25, y - 25), 2) 
                    pygame.draw.line(self.tela, cor_borda, (x + 20, y - 5), (x + 25, y - 25), 2) 
                    
                else:
                    rect_vis = pygame.Rect(x - 30, y - 20, 60, 40)
                    pygame.draw.rect(self.tela, cor_fundo, rect_vis, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, rect_vis, 2, border_radius=4)

                nome_lbl = self.fonte_m.render(nome[:8], True, COR_TEXTO)
                risco_lbl = self.fonte_p.render(f"Risco: {risco_efetivo}", True, cor_borda)
                severidade_lbl = self.fonte_p.render(
                    f"Sev: {severidade_principal}" if tem_alerta else "",
                    True,
                    cor_borda
                )
                
                offset_y_nome = -75 if tipo == "SERVIDOR" else -50
                offset_y_risco = 55 if tipo == "SERVIDOR" else 35
                
                self.tela.blit(nome_lbl, (x - nome_lbl.get_width()//2, y + offset_y_nome))
                self.tela.blit(risco_lbl, (x - risco_lbl.get_width()//2, y + offset_y_risco))
                if tem_alerta:
                    self.tela.blit(severidade_lbl, (x - severidade_lbl.get_width()//2, y + offset_y_risco + 16))

                if tem_alerta:
                    pygame.draw.circle(self.tela, (0,0,0), (x + 30, y - 30), 12)
                    pygame.draw.circle(self.tela, cor_borda, (x + 30, y - 30), 12, 2)
                    exc = self.fonte_m.render("!", True, cor_borda)
                    self.tela.blit(exc, (x + 26, y - 38))

                self.rects_matriz_risco.append((rect_clique, ativo))

            # 2. FILTRAR SERVIDORES E DESENHAR AS GAVETAS LATERAIS
            servidores = [a for a in self.ativos_brutos if a.get('tipo', '').upper() == 'SERVIDOR']
            
            if not self.servidor_foco_painel and servidores:
                self.servidor_foco_painel = str(servidores[0]['id'])
            
            servidores_visiveis = servidores[self.scroll_gaveta_servidores : self.scroll_gaveta_servidores + 9]
            
            for i, srv in enumerate(servidores_visiveis):
                r_gaveta = pygame.Rect(area_gavetas.x + 10, area_gavetas.y + 40 + (i * 45), 180, 35)
                
                esta_aberta = (self.servidor_foco_painel == str(srv['id']))
                cor_fundo = (30, 60, 90) if esta_aberta else (20, 30, 45)
                
                pygame.draw.rect(self.tela, cor_fundo, r_gaveta, border_radius=4)
                pygame.draw.rect(self.tela, COR_CIANO_NEON if esta_aberta else (40, 58, 85), r_gaveta, 1, border_radius=4)
                
                txt_srv = self.fonte_p.render(f"[{srv['id']}] {srv.get('nome', '')}", True, COR_TEXTO)
                self.tela.blit(txt_srv, (r_gaveta.x + 10, r_gaveta.y + 10))
                
                if r_gaveta.collidepoint(pos_mouse) and pygame.mouse.get_pressed()[0]:
                    self.servidor_foco_painel = str(srv['id'])

            # 3. DESENHAR A ÁRVORE PARA O SERVIDOR FOCADO
            if self.servidor_foco_painel:
                srv_alvo = next((s for s in servidores if str(s['id']) == self.servidor_foco_painel), None)
                
                if srv_alvo:
                    y_srv = area_arvore.y + 80
                    y_rot = area_arvore.y + 220
                    y_end = area_arvore.y + 360
                    
                    cx_srv = area_arvore.x + (area_arvore.width // 2)
                    
                    sala_focada_normalizada = str(srv_alvo.get('local', '')).strip().casefold()
                    ativos_da_sala = [
                        ativo for ativo in self.ativos_brutos
                        if str(ativo.get('local', '')).strip().casefold() == sala_focada_normalizada
                    ]
                    roteadores = [a for a in ativos_da_sala if a.get('tipo', '').upper() == 'ROTEADOR']
                    endpoints = [a for a in ativos_da_sala if a.get('tipo', '').upper() in ['NOTEBOOK', 'DESKTOP']]
                    
                    pos_roteadores = []
                    
                    if roteadores:
                        espaco_rot = area_arvore.width / (len(roteadores) + 1)
                        for i, rot in enumerate(roteadores):
                            rx = area_arvore.x + espaco_rot * (i + 1)
                            pos_roteadores.append((rx, y_rot, rot))
                            pygame.draw.line(self.tela, (60, 90, 120), (cx_srv, y_srv + 50), (rx, y_rot - 15), 2)
                            
                    if endpoints:
                        espaco_end = area_arvore.width / (len(endpoints) + 1)
                        for i, end in enumerate(endpoints):
                            ex = area_arvore.x + espaco_end * (i + 1)
                            
                            if pos_roteadores:
                                idx_rot = i % len(pos_roteadores)
                                rx_pai = pos_roteadores[idx_rot][0]
                                pygame.draw.line(self.tela, (40, 70, 90), (rx_pai, y_rot + 15), (ex, y_end - 25), 2)
                            else:
                                pygame.draw.line(self.tela, (40, 70, 90), (cx_srv, y_srv + 50), (ex, y_end - 25), 2)
                                
                            desenhar_icone_ativo(ex, y_end, end)

                    for rx, ry, rot in pos_roteadores:
                        desenhar_icone_ativo(rx, ry, rot)
                        
                    desenhar_icone_ativo(cx_srv, y_srv, srv_alvo)
            else:
                self.tela.blit(self.fonte_p.render("<- Crie ou selecione um servidor na gaveta lateral.", True, COR_TEXTO_MUTED), (area_arvore.x + 20, area_arvore.y + 20))

            if self.mensagem_status:
                self.tela.blit(self.fonte_m.render(self.mensagem_status, True, self.cor_status), (rect_modal.x + 30, rect_modal.y + 550))

        elif self.modal_ativo == "VULN_PATCH":
            self.tela.blit(self.fonte_g.render("TELA DE INCIDENTES // WORKSTATION ALVO", True, COR_VERMELHO_NEON), (rect_modal.x + 30, rect_modal.y + 24))
            self.tela.blit(self.fonte_p.render("REGISTRAR OU CORRIGIR VULNERABILIDADE:", True, COR_TEXTO_MUTED), (rect_modal.x + 30, rect_modal.y + 60))
            
            for campo in self.campos_vuln: campo.desenhar(self.tela)
            
            painel_ativos = pygame.Rect(600, 140, 400, 135)
            pygame.draw.rect(self.tela, (12, 18, 28), painel_ativos)
            pygame.draw.rect(self.tela, (30, 45, 68), painel_ativos, 2)
            self.tela.blit(self.fonte_m.render("INVENTÁRIO (SCROLL PARA SELECIONAR)", True, COR_CIANO_NEON), (painel_ativos.x + 10, painel_ativos.y + 10))

            self.rects_ativos_vuln = []
            inv_visiveis = self.ativos_brutos[self.scroll_vuln_inv : self.scroll_vuln_inv + 4]
            for i, d in enumerate(inv_visiveis):
                r_item = pygame.Rect(painel_ativos.x + 10, painel_ativos.y + 35 + (i * 24), 380, 20)
                pygame.draw.rect(self.tela, (25, 35, 50), r_item)
                pygame.draw.rect(self.tela, (40, 58, 85), r_item, 1)
                txt = f"ID: {d['id']} | {d.get('nome', '')} | {d.get('tipo', '')}"
                self.tela.blit(self.fonte_p.render(txt, True, COR_TEXTO), (r_item.x + 10, r_item.y + 3))
                self.rects_ativos_vuln.append((r_item, d))
            
            painel_vulns = pygame.Rect(600, 290, 400, 135)
            pygame.draw.rect(self.tela, (12, 18, 28), painel_vulns)
            pygame.draw.rect(self.tela, (40, 10, 15) if self.lista_vulns_ativas else (10, 40, 20), painel_vulns, 2)
            self.tela.blit(self.fonte_m.render("VULNERABILIDADES (SCROLL P/ CORRIGIR)", True, COR_AMBAR), (painel_vulns.x + 10, painel_vulns.y + 10))
            
            self.rects_vulns = []
            if not self.lista_vulns_ativas:
                self.tela.blit(self.fonte_p.render("SISTEMA SEGURO: Nenhuma falha detectada.", True, COR_VERDE_MATRIX), (painel_vulns.x + 10, painel_vulns.y + 40))
            else:
                vulns_visiveis = self.lista_vulns_ativas[self.scroll_vuln_lista : self.scroll_vuln_lista + 4]
                for i, v in enumerate(vulns_visiveis):
                    r_item = pygame.Rect(painel_vulns.x + 10, painel_vulns.y + 35 + (i * 24), 380, 20)
                    pygame.draw.rect(self.tela, (25, 10, 15), r_item)
                    pygame.draw.rect(self.tela, (60, 20, 30), r_item, 1)
                    
                    texto_vuln = f"ID:{v['id_ativo']} | {v['nome']} | CVE: {v['cve']} | {v['severidade'].upper()}"
                    
                    # CORREÇÃO DE COR DINÂMICA
                    sev_list = v['severidade'].lower()
                    if sev_list == 'baixa': cor_txt = COR_AMBAR
                    elif sev_list == 'media': cor_txt = COR_LARANJA
                    elif sev_list == 'alta': cor_txt = COR_VERMELHO_CLARO
                    else: cor_txt = COR_VERMELHO_ESCURO
                    
                    self.tela.blit(self.fonte_p.render(texto_vuln, True, cor_txt), (r_item.x + 10, r_item.y + 3))
                    self.rects_vulns.append((r_item, v))
            
            if self.mensagem_status:
                self.tela.blit(self.fonte_m.render(self.mensagem_status, True, self.cor_status), (280, 498))
                
            btn_patch = pygame.Rect(280, 520, 200, 48)
            pygame.draw.rect(self.tela, (60, 0, 0), btn_patch)
            pygame.draw.rect(self.tela, COR_VERMELHO_NEON, btn_patch, 2)
            self.tela.blit(self.fonte_m.render("REGISTRAR", True, COR_TEXTO), (btn_patch.x + 45, btn_patch.y + 14))

            btn_fix = pygame.Rect(500, 520, 200, 48)
            
            pode_corrigir = bool(self.vuln_log.texto.strip() and self.vuln_id.texto.strip())
            cor_fundo_fix = (0, 40, 0) if pode_corrigir else (20, 25, 30)
            cor_borda_fix = COR_VERDE_MATRIX if pode_corrigir else (60, 80, 100)
            cor_texto_fix = COR_TEXTO if pode_corrigir else (100, 120, 150)

            pygame.draw.rect(self.tela, cor_fundo_fix, btn_fix)
            pygame.draw.rect(self.tela, cor_borda_fix, btn_fix, 2)
            self.tela.blit(self.fonte_m.render("CORRIGIR", True, cor_texto_fix), (btn_fix.x + 55, btn_fix.y + 14))

            self.vuln_modelo.desenhar_menu(self.tela)

    # ==========================================
    # SUB-SESSÃO: LOOP DE EXECUÇÃO
    # ==========================================
    def executar(self):
        while self.rodando:
            self.processar_eventos()
            self.desenhar_cenario()
            self.desenhar_objetos()
            self.desenhar_modais()
            pygame.display.flip()
            self.relogio.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.executar()
