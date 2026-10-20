import datetime
import time
from ativos import Equipamento
from persistencia import ler_db
from vulnerabilidades import CATALOGO_VULNERABILIDADES
from CRUD.risco_salas import calcular_relatorio_risco_por_sala
from interface.configuracoes import (
    COR_VERDE_MATRIX,
    COR_CIANO_NEON,
    COR_AMBAR,
    COR_LARANJA,
    COR_VERMELHO_CLARO,
    COR_VERMELHO_ESCURO,
    CORRECOES_SUGERIDAS_VULN
)

# ==========================================
# SUB-SESSÃO: GERENCIAMENTO DE ESTADO E DADOS
# ==========================================
class GerenciadorEstado:
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

    def obter_sugestao_vuln(self, descricao, cve="", categoria=""):
        chave_desc = str(descricao).strip().casefold()
        if chave_desc in CORRECOES_SUGERIDAS_VULN:
            return CORRECOES_SUGERIDAS_VULN[chave_desc]

        chave_cve = str(cve).strip().upper()
        if chave_cve in self.sugestoes_nvd:
            return self.sugestoes_nvd[chave_cve]

        cat_up = str(categoria).strip().upper()
        desc_low = chave_desc
        if cat_up in ("CWE-89", "CWE-78", "CWE-77", "CWE-94") or "sql" in desc_low or "injection" in desc_low:
            acao = "Aplique o patch de segurança oficial e valide/parametrize entradas para bloquear injeção de comandos."
        elif cat_up == "CWE-79" or "xss" in desc_low or "cross-site scripting" in desc_low:
            acao = "Atualize o componente afetado e aplique sanitização de dados na exibição de páginas."
        elif cat_up in ("CWE-119", "CWE-120", "CWE-125", "CWE-787", "CWE-416") or "overflow" in desc_low or "memory" in desc_low:
            acao = "Instale a atualização oficial do fabricante para corrigir o tratamento de memória."
        elif cat_up in ("CWE-287", "CWE-306", "CWE-798", "CWE-862", "CWE-863", "CWE-269") or "auth" in desc_low or "privilege" in desc_low:
            acao = "Atualize o sistema afetado, restrinja permissões de acesso e revise as credenciais."
        elif cat_up in ("CWE-22", "CWE-200", "CWE-502") or "traversal" in desc_low:
            acao = "Aplique a correção do fabricante e bloqueie acessos indevidos a diretórios e arquivos."
        elif cat_up == "CWE-400" or "denial of service" in desc_low or "dos" in desc_low:
            acao = "Atualize o serviço vulnerável e aplique limite de conexões no firewall."
        else:
            acao = "Aplique o pacote de correção oficial do fabricante e restrinja o acesso ao serviço vulnerável."

        if chave_cve and chave_cve != "N/A":
            return f"{acao} Consulte o boletim oficial da {chave_cve} na NVD."
        return acao

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
        if vulnerabilidade.get('sugestao_correcao') and vulnerabilidade.get('cve'):
            self.sugestoes_nvd[str(vulnerabilidade['cve']).upper()] = vulnerabilidade['sugestao_correcao']
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
            if not erro and pagina:
                for item in pagina.get('vulnerabilidades', []):
                    if item.get('cve') and item.get('sugestao_correcao'):
                        self.sugestoes_nvd[str(item['cve']).upper()] = item['sugestao_correcao']
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

        if hasattr(self, "upd_loc"):
            opcoes_upd = [("Manter local atual", "")] + [
                (sala, sala) for sala in salas if not any(c.isdigit() for c in sala)
            ]
            valor_upd = self.upd_loc.texto
            self.upd_loc.definir_opcoes(opcoes_upd)
            if valor_upd not in {valor for _, valor in opcoes_upd}:
                valor_upd = ""
            self.upd_loc.definir_valor(valor_upd)

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
            
            if vulns_em_aberto:
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
            
        servidores_ids = [str(a['id']) for a in self.ativos_brutos if a.get('tipo', '').upper() == 'SERVIDOR']
        if getattr(self, 'servidor_foco_painel', None) not in servidores_ids:
            self.servidor_foco_painel = servidores_ids[0] if servidores_ids else None

        ids_todos = [str(a['id']) for a in self.ativos_brutos]
        if getattr(self, 'ativo_inspecionado_servidor', None) not in ids_todos:
            self.ativo_inspecionado_servidor = self.servidor_foco_painel

        ativo_insp = next(
            (a for a in self.ativos_brutos if str(a.get('id', '')) == str(getattr(self, 'ativo_inspecionado_servidor', ''))),
            None
        )
        if ativo_insp:
            abertas_insp = [v for v in ativo_insp.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]
            vuln_atual = getattr(self, 'vuln_selecionada_servidor', None)
            if not vuln_atual or not any(
                str(v.get('cve', '')).upper() == str(vuln_atual.get('cve', '')).upper()
                and str(v.get('descricao', '')) == str(vuln_atual.get('descricao', ''))
                for v in abertas_insp
            ):
                self.vuln_selecionada_servidor = abertas_insp[0] if abertas_insp else None
        else:
            self.vuln_selecionada_servidor = None
            
        try:
            self.relatorio_risco = calcular_relatorio_risco_por_sala()
        except Exception as e:
            self.relatorio_risco = [
                "[ERRO CRÍTICO] Falha ao calcular a Matriz de Risco.",
                "Motivo: Possível banco de dados vazio ou sem dependências.",
                f"Detalhe Técnico: {str(e)}"
            ]

