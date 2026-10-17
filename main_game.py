import sys
import random
import pygame
from ativos import Equipamento
from vulnerabilidades import CATALOGO_VULNERABILIDADES
from integracoes.nvd_api import NvdCveSearchWorker
from interface.configuracoes import *
from interface.componentes import CaixaTexto, CaixaSelecao
from interface.estado import GerenciadorEstado
from interface.eventos import ProcessadorEventos
from interface.renderizacao import RenderizadorGrafico

# ==========================================
# SESSÃO: CLASSE PRINCIPAL DO SISTEMA (APP)
# ==========================================
class App(GerenciadorEstado, ProcessadorEventos, RenderizadorGrafico):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(200, 50) 
        
        self.servidor_foco_painel = None
        self.ativo_inspecionado_servidor = None
        self.vuln_selecionada_servidor = None
        self.rects_vulns_servidor = []
        self.descricao_expandida = False

        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JANELA)
        pygame.mouse.set_visible(False)
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
        self.scroll_vuln_servidor = 0
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

        self.upd_id = CaixaTexto(300, 200, 300, 32, "ID ou Nome do Ativo")
        self.upd_resp = CaixaTexto(300, 250, 300, 32, "Novo Responsável (Opcional)")
        opcoes_upd_salas = [("Manter local atual", "")] + [(f"Sala {letra}", f"Sala {letra}") for letra in "ABCD"]
        self.upd_loc = CaixaSelecao(300, 300, 300, 32, "Nova Localidade", opcoes_upd_salas, "")
        self.campos_upd = [self.upd_id, self.upd_resp, self.upd_loc]

        self.rem_id = CaixaTexto(300, 250, 300, 32, "ID ou Nome do Ativo")
        self.campos_rem = [self.rem_id]
        self.consulta_busca = CaixaTexto(300, 175, 690, 28, "Buscar usuário, nome ou patrimônio")
        self.ativo_consulta_selecionado = None

        opcoes_vulnerabilidade = [("Selecione uma vulnerabilidade", "")]
        opcoes_vulnerabilidade.extend((item['nome'], item['id']) for item in CATALOGO_VULNERABILIDADES)
        self.vuln_id = CaixaTexto(280, 145, 300, 28, "Ativo Selecionado", somente_leitura=True)
        self.vuln_modelo = CaixaSelecao(280, 190, 300, 28, "Vulnerabilidade", opcoes_vulnerabilidade, "", mostrar_rotulo=False, permitir_busca=True)
        self.vuln_cve = CaixaTexto(280, 235, 300, 28, "Código CVE", somente_leitura=True)
        self.vuln_desc = CaixaTexto(280, 280, 300, 28, "Nome da Falha", somente_leitura=True)
        self.vuln_cat = CaixaTexto(280, 325, 300, 28, "Categoria", somente_leitura=True)
        opcoes_severidade = [("Aguardando seleção", "")] + [(nome, valor) for nome, valor in [("Baixa", "baixa"), ("Média", "media"), ("Alta", "alta"), ("Crítica", "critica")]]
        self.vuln_sev = CaixaSelecao(280, 370, 300, 28, "Gravidade", opcoes_severidade, "", bloqueado=True)
        self.vuln_stat = CaixaSelecao(280, 415, 300, 28, "Situação", [("Aberta", Equipamento.STATUS_ABERTO), ("Corrigida", Equipamento.STATUS_FECHADO)], Equipamento.STATUS_ABERTO, bloqueado=True)
        self.vuln_log = CaixaTexto(763, 478, 244, 42, "Descreva a correção feita")
        self.campos_vuln = [self.vuln_id, self.vuln_modelo, self.vuln_cve, self.vuln_desc, self.vuln_cat, self.vuln_sev, self.vuln_stat]
        self.vulnerabilidades_disponiveis = {item['id']: item for item in CATALOGO_VULNERABILIDADES}
        self.resultados_nvd = []
        self.sugestoes_nvd = {}
        self.total_resultados_nvd = 0
        self.proximo_indice_nvd = 0
        self.busca_nvd_pendente = ""
        self.busca_nvd_inicio_pendente = 0
        self.busca_nvd_disparar_em = 0.0
        self.worker_nvd = NvdCveSearchWorker()

        self.adicionar_log("SISTEMA", "PAINEL", "Sistema de Monitoramento Inicializado.")
        self.sincronizar_dados()

    # ==========================================
    # SUB-SESSÃO: LOOP DE EXECUÇÃO
    # ==========================================
    def executar(self):
        while self.rodando:
            self.processar_eventos()
            self.desenhar_cenario()
            self.desenhar_objetos()
            self.desenhar_modais()
            self.desenhar_cursor()
            pygame.display.flip()
            self.relogio.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.executar()