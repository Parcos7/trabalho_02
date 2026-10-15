import sys
import math
import random
import datetime
import pygame
from persistencia import ler_db
from CRUD.cadastro import cadastrar_ativo
from CRUD.atualizar import atualizar_ativo
from CRUD.remover import remover_ativo
from vulnerabilidades import registrar_vulnerabilidade, corrigir_vulnerabilidade
from CRUD.risco import calcular_risco_global

# ==========================================
# SESSÃO: CONFIGURAÇÕES GERAIS E CONSTANTES
# ==========================================
LARGURA_TELA = 1280
ALTURA_TELA = 720
TITULO_JANELA = "CyberPixel - SOC Level 3 [Visual Interface]"
FPS = 50

# Paleta de Cores
COR_FUNDO = (0, 0, 0)
COR_CHAO = (5, 5, 5)
COR_GRADE = (0, 40, 0)
COR_PAREDE = (0, 0, 0)
COR_TEXTO = (0, 255, 0)
COR_TEXTO_MUTED = (0, 150, 0)
COR_CIANO_NEON = (0, 255, 0)
COR_VERDE_MATRIX = (0, 255, 0)
COR_AMBAR = (200, 200, 0)
COR_LARANJA = (255, 140, 0)
COR_VERMELHO_NEON = (255, 0, 0)
COR_PAINEL = (0, 0, 0)
COR_PAINEL_BORDA = (0, 255, 0)

# ==========================================
# SESSÃO: COMPONENTES DE INTERFACE (UI)
# ==========================================
class CaixaTexto:
    def __init__(self, x, y, largura, altura, rotulo):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_ativa = COR_CIANO_NEON
        self.cor_inativa = (40, 58, 85)
        self.cor = self.cor_inativa
        self.texto = ''
        self.rotulo = rotulo
        self.ativo = False
        self.fonte = pygame.font.SysFont("Consolas", 14)

    def processar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos):
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
                if char and char not in ['´', '`', '~', '^', '¨']:
                    self.texto += char

    def desenhar(self, tela):
        pygame.draw.rect(tela, (15, 20, 30), self.rect)
        pygame.draw.rect(tela, self.cor, self.rect, 2)
        
        if self.texto:
            img_txt = self.fonte.render(self.texto, True, COR_TEXTO)
        else:
            img_txt = self.fonte.render(self.rotulo, True, COR_TEXTO_MUTED)
            
        tela.blit(img_txt, (self.rect.x + 8, self.rect.y + 8))

# ==========================================
# SESSÃO: CLASSE PRINCIPAL DO SISTEMA (APP)
# ==========================================
class App:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(200, 50) 
        
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
        
        self.historico_logs = []
        self.scroll_logs = 0
        self.scroll_crud_ativos = 0
        self.scroll_vuln_inv = 0
        self.scroll_vuln_lista = 0
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
        
        self.cad_id = CaixaTexto(300, 175, 300, 28, "ID (Apenas Números)")
        self.cad_host = CaixaTexto(300, 220, 300, 28, "Hostname (Ex: NOTP01)")
        self.cad_resp = CaixaTexto(300, 265, 300, 28, "Responsável (Sem números)")
        self.cad_loc = CaixaTexto(300, 310, 300, 28, "Localidade")
        self.cad_extra = CaixaTexto(300, 355, 300, 28, "Dado Extra (SO, RAM ou FW)")
        self.campos_cad = [self.cad_id, self.cad_host, self.cad_resp, self.cad_loc, self.cad_extra]

        self.upd_id = CaixaTexto(300, 200, 300, 32, "ID ou Hostname do Ativo")
        self.upd_resp = CaixaTexto(300, 250, 300, 32, "Novo Responsável (Opcional)")
        self.upd_loc = CaixaTexto(300, 300, 300, 32, "Nova Localidade (Opcional)")
        self.campos_upd = [self.upd_id, self.upd_resp, self.upd_loc]

        self.rem_id = CaixaTexto(300, 250, 300, 32, "ID ou Hostname do Ativo")
        self.campos_rem = [self.rem_id]

        self.vuln_id = CaixaTexto(280, 160, 300, 28, "ID ou Hostname do Alvo")
        self.vuln_cve = CaixaTexto(280, 200, 300, 28, "Código CVE (Opcional)")
        self.vuln_desc = CaixaTexto(280, 240, 300, 28, "Descrição (Ex: Senha fraca)")
        self.vuln_cat = CaixaTexto(280, 280, 300, 28, "Categoria (Rede, Hardware)")
        self.vuln_sev = CaixaTexto(280, 320, 300, 28, "Severidade (baixa/media/alta/critica)")
        self.vuln_stat = CaixaTexto(280, 360, 300, 28, "Status (aberta/corrigida...)")
        self.vuln_log = CaixaTexto(280, 400, 300, 28, "Log da Correção (Obrigatório p/ Corrigir)")
        self.campos_vuln = [self.vuln_id, self.vuln_cve, self.vuln_desc, self.vuln_cat, self.vuln_sev, self.vuln_stat, self.vuln_log]

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

    def sincronizar_dados(self):
        db_inventario = ler_db()
        self.lista_ativos_display = []
        self.lista_vulns_ativas = []
        self.ativos_brutos = []
        self.alerta_ativo = False
        self.cor_alerta_atual = COR_VERDE_MATRIX
        
        pesos_severidade = {'baixa': 1, 'media': 2, 'alta': 3, 'critica': 4}
        max_peso = 0
        
        for id_ativo, dados in db_inventario.items():
            self.ativos_brutos.append(dados)
            vulns = dados.get('vulnerabilidades', [])
            
            vulns_em_aberto = [v for v in vulns if v.get('status', '').lower() != 'corrigida']
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
            
        if max_peso == 1:
            self.cor_alerta_atual = COR_AMBAR 
            self.nivel_alerta_str = "ALERTA BAIXO"
        elif max_peso == 2:
            self.cor_alerta_atual = COR_LARANJA 
            self.nivel_alerta_str = "ALERTA MÉDIO"
        elif max_peso >= 3:
            self.cor_alerta_atual = COR_VERMELHO_NEON 
            self.nivel_alerta_str = "ALERTA CRÍTICO!"
        else:
            self.cor_alerta_atual = COR_VERDE_MATRIX
            self.nivel_alerta_str = "WORKSTATION SEGURA"
            
        try:
            self.relatorio_risco = calcular_risco_global()
        except Exception:
            self.relatorio_risco = ["[ERRO] Motor de álgebra linear indisponível."]

# ==========================================
# SUB-SESSÃO: PROCESSAMENTO DE EVENTOS (CONTROLLER)
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

                if pygame.Rect(320, 520, 340, 44).collidepoint(pos_mouse):
                    if self.aba_crud_ativa == "LISTAR":
                        self.sincronizar_dados()
                        self.definir_mensagem("Dados atualizados do JSON.", COR_CIANO_NEON)
                        
                    elif self.aba_crud_ativa == "CADASTRAR":
                        resp_limpo = self.cad_resp.texto.strip()
                        loc_limpo = self.cad_loc.texto.strip()
                        if any(char.isdigit() for char in resp_limpo):
                            self.definir_mensagem("ERRO VALIDAÇÃO: O responsável não pode ter números.", COR_VERMELHO_NEON)
                            return
                        if any(char.isdigit() for char in loc_limpo):
                            self.definir_mensagem("ERRO VALIDAÇÃO: A localidade não pode conter números.", COR_VERMELHO_NEON)
                            return

                        host = self.cad_host.texto.lower().strip()
                        tipo_auto = ""
                        if host.startswith("notp"): tipo_auto = "NOTEBOOK"
                        elif host.startswith("serv"): tipo_auto = "SERVIDOR"
                        elif host.startswith("micp"): tipo_auto = "DESKTOP"
                        elif host.startswith("rotp"): tipo_auto = "ROTEADOR"
                        
                        if not tipo_auto:
                            self.definir_mensagem("ERRO: O Hostname deve iniciar com NOTP, SERV, MICP ou ROTP.", COR_VERMELHO_NEON)
                        else:
                            sucesso = cadastrar_ativo(self.cad_id.texto, self.cad_host.texto, self.cad_resp.texto, self.cad_loc.texto, tipo_auto, self.cad_extra.texto)
                            if sucesso:
                                self.adicionar_log("CADASTRO", host.upper(), f"Ativo do tipo {tipo_auto} inserido no inventário.")
                                for c in self.campos_cad: c.texto = ""
                                self.definir_mensagem(f"SUCESSO: Ativo ({tipo_auto}) cadastrado!", COR_VERDE_MATRIX)
                            else:
                                self.definir_mensagem("ERRO: Dados duplicados, vazios ou incorretos.", COR_VERMELHO_NEON)
                        self.sincronizar_dados()
                        
                    elif self.aba_crud_ativa == "ATUALIZAR":
                        resp_limpo = self.upd_resp.texto.strip()
                        loc_limpo = self.upd_loc.texto.strip()
                        
                        if resp_limpo and any(char.isdigit() for char in resp_limpo):
                            self.definir_mensagem("ERRO VALIDAÇÃO: O responsável não pode ter números.", COR_VERMELHO_NEON)
                            return
                        if loc_limpo and any(char.isdigit() for char in loc_limpo):
                            self.definir_mensagem("ERRO VALIDAÇÃO: A localidade não pode conter números.", COR_VERMELHO_NEON)
                            return

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
                            self.definir_mensagem("ERRO: ID não encontrado ou entrada inválida.", COR_VERMELHO_NEON)
                        self.sincronizar_dados()
                        
                    elif self.aba_crud_ativa == "REMOVER":
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
                            self.definir_mensagem("ERRO: ID não encontrado no sistema.", COR_VERMELHO_NEON)
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
                for r_item, d in self.rects_ativos_vuln:
                    if r_item.collidepoint(pos_mouse):
                        self.vuln_id.texto = str(d['id'])
                        self.vuln_cve.texto = ""
                        self.vuln_desc.texto = ""
                        self.vuln_log.texto = ""
                        self.definir_mensagem(f"ALVO: {d['nome']}. Preencha os dados e registre a falha.", COR_AMBAR)
                        return

                for r_item, v in self.rects_vulns:
                    if r_item.collidepoint(pos_mouse):
                        self.vuln_id.texto = str(v['id_ativo'])
                        self.vuln_cve.texto = v['cve']
                        self.vuln_desc.texto = v['descricao']
                        self.vuln_cat.texto = v['categoria']
                        self.vuln_sev.texto = v['severidade']
                        self.vuln_stat.texto = v['status']
                        self.vuln_log.texto = ""
                        self.definir_mensagem(f"SELECIONADO: {v['nome']}. Descreva no Log o que fará para corrigir.", COR_AMBAR)
                        return

                rect_btn_registrar = pygame.Rect(280, 520, 200, 48)
                rect_btn_corrigir = pygame.Rect(500, 520, 200, 48)
                
                if rect_btn_registrar.collidepoint(pos_mouse):
                    alvo = self.vuln_id.texto.strip().lower()
                    id_resolvido = alvo
                    for d in self.ativos_brutos:
                        if str(d.get('id', '')).lower() == alvo or d.get('nome', '').lower() == alvo:
                            id_resolvido = str(d.get('id', ''))
                            break

                    sucesso = registrar_vulnerabilidade(id_resolvido, self.vuln_cve.texto, self.vuln_desc.texto, self.vuln_cat.texto, self.vuln_sev.texto, self.vuln_stat.texto)
                    if sucesso:
                        self.adicionar_log("INCIDENTE", id_resolvido, f"Nova falha reportada. CVE: {self.vuln_cve.texto}")
                        for c in self.campos_vuln: c.texto = ""
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
                            
                    sucesso = corrigir_vulnerabilidade(id_resolvido, self.vuln_cve.texto)
                    if sucesso:
                        self.adicionar_log("CORREÇÃO", id_resolvido, log_texto)
                        for c in self.campos_vuln: c.texto = ""
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
            if self.aba_crud_ativa == "CADASTRAR": campos_ativos = self.campos_cad
            elif self.aba_crud_ativa == "ATUALIZAR": campos_ativos = self.campos_upd
            elif self.aba_crud_ativa == "REMOVER": campos_ativos = self.campos_rem
        elif self.modal_ativo == "VULN_PATCH":
            campos_ativos = self.campos_vuln

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
                campo.processar_evento(evento)

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                self.tratar_clique(pos_mouse)

# ==========================================
# SUB-SESSÃO: RENDERIZAÇÃO GRÁFICA (VIEW)
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
                cor_led = COR_VERMELHO_NEON if led_aceso else (80, 10, 20)
            else:
                cor_led = COR_VERDE_MATRIX if led_aceso else COR_AMBAR
                
            pygame.draw.circle(self.tela, cor_led, (r_blade.x + 150, r_blade.y + 18), 4)
            
        self.tela.blit(self.fonte_p.render("[ SERVIDOR: JSON / RISCO ]", True, COR_AMBAR), (self.rect_servidor.x, self.rect_servidor.y - 22))

        piscar = self.alerta_ativo and ((ticks // 250) % 2 == 0)
        cor_pc = COR_VERMELHO_NEON if piscar else (COR_CIANO_NEON if self.objeto_em_hover == "WORKSTATION" else (45, 65, 95))
        fundo_tela = (80, 10, 20) if piscar else ((15, 30, 45) if self.objeto_em_hover == "WORKSTATION" else (15, 22, 35))
        rect_pc_tela = pygame.Rect(self.rect_workstation.x + 20, self.rect_workstation.y, 150, 105)
        pygame.draw.rect(self.tela, fundo_tela, rect_pc_tela)
        pygame.draw.rect(self.tela, cor_pc, rect_pc_tela, 3 if self.alerta_ativo else 2)
        pygame.draw.rect(self.tela, (30, 45, 65), (self.rect_workstation.x + 85, self.rect_workstation.y + 105, 20, 25))
        pygame.draw.rect(self.tela, (30, 45, 65), (self.rect_workstation.x + 65, self.rect_workstation.y + 125, 60, 10))
        rotulo_pc = "ALERTA CRÍTICO!" if self.alerta_ativo else "WORKSTATION SEGURA"
        self.tela.blit(self.fonte_p.render(f"[ {rotulo_pc} ]", True, COR_VERMELHO_NEON if self.alerta_ativo else COR_VERDE_MATRIX), (self.rect_workstation.x, self.rect_workstation.y - 20))

        if self.alerta_ativo:
            bug_x = self.rect_workstation.x + 75
            bug_y = self.rect_workstation.y - 65 + int(math.sin(ticks / 140.0) * 8)
            
            pygame.draw.rect(self.tela, (40, 8, 16), (bug_x - 14, bug_y - 4, 46, 38))
            pygame.draw.rect(self.tela, COR_VERMELHO_NEON, (bug_x - 14, bug_y - 4, 46, 38), 2)
            
            try: 
                self.tela.blit(self.fonte_emoji.render("👾", True, (255, 255, 255)), (bug_x - 6, bug_y - 2))
            except Exception: 
                self.tela.blit(self.fonte_g.render("!", True, COR_VERMELHO_NEON), (bug_x + 2, bug_y))

            pygame.draw.rect(self.tela, (12, 18, 28), self.rect_telao)
            pygame.draw.rect(self.tela, COR_CIANO_NEON if self.objeto_em_hover == "TELAO" else (30, 48, 75), self.rect_telao, 2)
            
            fase_telao = (ticks // 10000) % 2 
            titulo_telao = "DASHBOARD [AUDITORIA]: LOGS EM TEMPO REAL" if fase_telao == 0 else "DASHBOARD [AMEAÇAS]: VULNERABILIDADES ATIVAS"
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
                        self.tela.blit(self.fonte_p.render(txt_vuln, True, COR_VERMELHO_NEON), (area_rolagem.x + 5, pos_y_atual))
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
            self.tela.blit(self.fonte_g.render("GERENCIADOR DE ATIVOS // CRUD VIEW", True, COR_CIANO_NEON), (rect_modal.x + 30, rect_modal.y + 24))
            
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
                self.tela.blit(self.fonte_p.render("DADOS VINCULADOS AO ARQUIVO JSON:", True, COR_TEXTO_MUTED), (corpo.x + 20, corpo.y + 10))
                if not self.lista_ativos_display:
                    self.tela.blit(self.fonte_p.render("Nenhum ativo cadastrado. Vá em CADASTRAR.", True, COR_TEXTO), (corpo.x + 20, corpo.y + 40))
                else:
                    for i, it in enumerate(self.lista_ativos_display[:10]): 
                        self.tela.blit(self.fonte_p.render(it, True, COR_VERMELHO_NEON if "ALERTA" in it else COR_TEXTO), (corpo.x + 20, corpo.y + 40 + i * 24))
            
            elif self.aba_crud_ativa == "CADASTRAR":
                for campo in self.campos_cad: 
                    campo.desenhar(self.tela)
                    
                col_x = 630
                col_y = 190
                self.tela.blit(self.fonte_m.render("PADRÃO AUTOMÁTICO DE ATIVOS", True, COR_AMBAR), (col_x, col_y))
                self.tela.blit(self.fonte_p.render("O tipo é deduzido pelo Hostname:", True, COR_CIANO_NEON), (col_x, col_y + 30))
                self.tela.blit(self.fonte_p.render("• NOTP... = Notebook", True, COR_TEXTO_MUTED), (col_x, col_y + 50))
                self.tela.blit(self.fonte_p.render("• SERV... = Servidor", True, COR_TEXTO_MUTED), (col_x, col_y + 70))
                self.tela.blit(self.fonte_p.render("• MICP... = Desktop", True, COR_TEXTO_MUTED), (col_x, col_y + 90))
                self.tela.blit(self.fonte_p.render("• ROTP... = Roteador", True, COR_TEXTO_MUTED), (col_x, col_y + 110))
                
                self.tela.blit(self.fonte_p.render("Regras de Dados Extras:", True, COR_CIANO_NEON), (col_x, col_y + 150))
                self.tela.blit(self.fonte_p.render("• Desktop/Note: RAM (Ex: 16)", True, COR_TEXTO_MUTED), (col_x, col_y + 170))
                self.tela.blit(self.fonte_p.render("• Servidor: SO (Ex: Linux)", True, COR_TEXTO_MUTED), (col_x, col_y + 190))
                self.tela.blit(self.fonte_p.render("• Roteador: FW (S/N)", True, COR_TEXTO_MUTED), (col_x, col_y + 210))
                
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
            self.tela.blit(self.fonte_g.render("INFRAESTRUTURA E MOTOR ALGÉBRICO AUTOMÁTICO", True, COR_AMBAR), (rect_modal.x + 30, rect_modal.y + 24))
            self.tela.blit(self.fonte_p.render("Topologia de Risco: Clique nos equipamentos para analisar a matriz.", True, COR_TEXTO_MUTED), (rect_modal.x + 30, rect_modal.y + 55))
            
            info_lines = [l for l in self.relatorio_risco if "Matriz M" in l or "Determ" in l]
            titulo_matriz = self.fonte_p.render("[STATUS DA REDE GLOBAL] MOTOR ALGÉBRICO INICIALIZADO:", True, COR_CIANO_NEON)
            self.tela.blit(titulo_matriz, (rect_modal.x + 30, rect_modal.y + 85))

            for i, line in enumerate(info_lines):
                clean_line = line.replace("=================== RELATÓRIO DE RISCO GLOBAL ===================", "").strip()
                if clean_line:
                    self.tela.blit(self.fonte_p.render(f"> {clean_line}", True, COR_TEXTO_MUTED), (rect_modal.x + 30, rect_modal.y + 105 + i * 20))

            cx = rect_modal.x + rect_modal.width // 2
            cy = rect_modal.y + rect_modal.height // 2 + 30
            
            servidor = next((a for a in self.ativos_brutos if a.get('tipo', '').upper() == 'SERVIDOR'), None)
            outros_ativos = [a for a in self.ativos_brutos if a.get('tipo', '').upper() != 'SERVIDOR']
            
            self.rects_matriz_risco = []
            angulo_passo = 2 * math.pi / len(outros_ativos) if outros_ativos else 0
            raio = 160

            def obter_risco_efetivo(nome_busca):
                for linha in self.relatorio_risco:
                    if f"[{nome_busca.lower()}" in linha.lower():
                        try: return linha.split("Risco Efetivo:")[-1].strip()
                        except: pass
                return "0.00"

            def desenhar_icone_ativo(x, y, ativo, is_center=False):
                tipo = ativo.get('tipo', '').upper()
                nome = ativo.get('nome', 'UNK').upper()
                risco_efetivo = obter_risco_efetivo(nome)
                
                vulns_abertas = [v for v in ativo.get('vulnerabilidades', []) if v.get('status', '').lower() != 'corrigida']
                tem_alerta = len(vulns_abertas) > 0
                
                cor_borda = COR_VERMELHO_NEON if tem_alerta else COR_VERDE_MATRIX
                cor_fundo = (40, 10, 10) if tem_alerta else (15, 25, 35)
                
                rect_clique = pygame.Rect(x - 40, y - 80, 80, 160) if is_center else pygame.Rect(x - 40, y - 40, 80, 80)
                if rect_clique.collidepoint(pos_mouse):
                    cor_fundo = (80, 20, 20) if tem_alerta else (30, 45, 65)

                if tipo == "SERVIDOR" or is_center:
                    rect_vis = pygame.Rect(x - 35, y - 70, 70, 140)
                    pygame.draw.rect(self.tela, cor_fundo, rect_vis, border_radius=8)
                    pygame.draw.rect(self.tela, cor_borda, rect_vis, 2, border_radius=8)
                    for j in range(4):
                        pygame.draw.line(self.tela, cor_borda, (x - 25, y - 40 + j*25), (x + 25, y - 40 + j*25), 2)
                        
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
                
                offset_y_nome = -95 if is_center else -50
                offset_y_risco = 80 if is_center else 35
                
                self.tela.blit(nome_lbl, (x - nome_lbl.get_width()//2, y + offset_y_nome))
                self.tela.blit(risco_lbl, (x - risco_lbl.get_width()//2, y + offset_y_risco))

                if tem_alerta:
                    pygame.draw.circle(self.tela, (0,0,0), (x + 30, y - 30), 12)
                    pygame.draw.circle(self.tela, COR_VERMELHO_NEON, (x + 30, y - 30), 12, 2)
                    exc = self.fonte_m.render("!", True, COR_VERMELHO_NEON)
                    self.tela.blit(exc, (x + 26, y - 38))

                self.rects_matriz_risco.append((rect_clique, ativo))

            for i, ativo in enumerate(outros_ativos):
                theta = i * angulo_passo
                x = cx + raio * math.cos(theta)
                y = cy + raio * math.sin(theta)
                pygame.draw.line(self.tela, (40, 60, 80), (cx, cy), (x, y), 2)

            for i, ativo in enumerate(outros_ativos):
                theta = i * angulo_passo
                x = cx + raio * math.cos(theta)
                y = cy + raio * math.sin(theta)
                desenhar_icone_ativo(x, y, ativo, False)

            if servidor:
                desenhar_icone_ativo(cx, cy, servidor, True)
            else:
                pygame.draw.circle(self.tela, (30, 45, 68), (int(cx), int(cy)), 50)
                pygame.draw.circle(self.tela, COR_CIANO_NEON, (int(cx), int(cy)), 50, 2)
                lbl = self.fonte_m.render("SEM SERVIDOR", True, COR_CIANO_NEON)
                self.tela.blit(lbl, (cx - lbl.get_width()//2, cy - 8))

            if self.mensagem_status:
                self.tela.blit(self.fonte_m.render(self.mensagem_status, True, self.cor_status), (rect_modal.x + 30, rect_modal.y + 480))

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
                    
                    texto_vuln = f"ID:{v['id_ativo']} | {v['nome']} | CVE: {v['cve']}"
                    
                    sev_list = v['severidade'].lower()
                    if sev_list == 'baixa': cor_txt = COR_AMBAR
                    elif sev_list == 'media': cor_txt = COR_LARANJA
                    else: cor_txt = COR_VERMELHO_NEON
                    
                    self.tela.blit(self.fonte_p.render(texto_vuln, True, cor_txt), (r_item.x + 10, r_item.y + 3))
                    self.rects_vulns.append((r_item, v))
            
            if self.mensagem_status:
                self.tela.blit(self.fonte_m.render(self.mensagem_status, True, self.cor_status), (280, 490))
                
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