import pygame
from ativos import Equipamento
from CRUD.cadastro import cadastrar_ativo
from CRUD.atualizar import atualizar_ativo
from CRUD.remover import remover_ativo
from vulnerabilidades import CATALOGO_VULNERABILIDADES, registrar_vulnerabilidade, corrigir_vulnerabilidade
from interface.configuracoes import (
    LARGURA_TELA,
    ALTURA_TELA,
    COR_VERDE_MATRIX,
    COR_AMBAR,
    COR_LARANJA,
    COR_VERMELHO_NEON,
    CORRECOES_SUGERIDAS_VULN
)

# ==========================================
# SUB-SESSÃO: PROCESSAMENTO DE EVENTOS
# ==========================================
class ProcessadorEventos:
    def tratar_clique(self, pos_mouse):
        if self.modal_ativo:
            rect_modal = pygame.Rect(250, 60, LARGURA_TELA - 500, ALTURA_TELA - 120)
            rect_fechar = pygame.Rect(rect_modal.right - 48, rect_modal.y + 16, 32, 32)
            
            if rect_fechar.collidepoint(pos_mouse):
                self.modal_ativo = None
                self.descricao_expandida = False
                self.mensagem_status = "" 
                return

            if self.descricao_expandida:
                if self.modal_ativo == "SERVIDOR_INFRA" and self.vuln_selecionada_servidor:
                    rect_btn_sugestao = pygame.Rect(340, 505, 310, 42)
                    if rect_btn_sugestao.collidepoint(pos_mouse):
                        v_sel = self.vuln_selecionada_servidor
                        self.vuln_log.texto = self.obter_sugestao_vuln(
                            v_sel.get('descricao', ''),
                            v_sel.get('cve', ''),
                            v_sel.get('categoria', '')
                        )
                        self.descricao_expandida = False
                        self.definir_mensagem("Sugestão preenchida! Clique em CORRIGIR FALHA.", COR_VERDE_MATRIX)
                        return
                self.descricao_expandida = False
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
                                self.upd_loc.definir_valor("")
                                self.upd_loc.menu_aberto = False
                            elif self.aba_crud_ativa == "REMOVER":
                                self.rem_id.texto = str(d['id'])
                            self.definir_mensagem(f"Ativo selecionado: {d['nome']}. Clique em confirmar.", COR_AMBAR)
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
                            self.definir_mensagem("O nome do responsável não pode conter números.", COR_VERMELHO_NEON)
                            return
                        local_sem_formatacao = loc_limpo.replace(" ", "").replace("-", "")
                        if not local_sem_formatacao.isalnum():
                            self.definir_mensagem("A localidade aceita apenas letras, números, espaços e hífens.", COR_VERMELHO_NEON)
                            return

                        prefixo = self.prefixos_hostname[tipo_ativo]
                        hostname = f"{prefixo}{patrimonio}"
                        if any(str(ativo.get('nome', '')).casefold() == hostname.casefold() for ativo in self.ativos_brutos):
                            self.definir_mensagem(f"Nome {hostname} já cadastrado. Informe outro patrimônio.", COR_VERMELHO_NEON)
                            return

                        dado_extra = self.cad_extra.texto.strip()
                        if tipo_ativo in ("NOTEBOOK", "DESKTOP") and (not dado_extra.isdigit() or int(dado_extra) < 1):
                            self.definir_mensagem("Informe a memória RAM em GB usando um número inteiro.", COR_VERMELHO_NEON)
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
                            self.definir_mensagem(f"Sucesso: Ativo ({tipo_ativo}) cadastrado!", COR_VERDE_MATRIX)
                        else:
                            self.definir_mensagem("Cadastro não concluído. Confira os dados informados.", COR_VERMELHO_NEON)
                        self.sincronizar_dados()
                        if sucesso:
                            self.cad_loc.definir_valor(loc_limpo)
                        
                    elif self.aba_crud_ativa == "ATUALIZAR":
                        resp_limpo = self.upd_resp.texto.strip()
                        loc_limpo = self.upd_loc.texto.strip()
                        
                        if resp_limpo and any(char.isdigit() for char in resp_limpo):
                            self.definir_mensagem("O nome do responsável não pode conter números.", COR_VERMELHO_NEON)
                            return
                        if loc_limpo and any(char.isdigit() for char in loc_limpo):
                            self.definir_mensagem("A localidade não pode conter números.", COR_VERMELHO_NEON)
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
                            self.upd_id.texto = ""
                            self.upd_resp.texto = ""
                            self.upd_loc.definir_valor("")
                            self.definir_mensagem("Sucesso: Dados do ativo atualizados!", COR_VERDE_MATRIX)
                        else:
                            self.definir_mensagem("Ativo não encontrado ou dados inválidos.", COR_VERMELHO_NEON)
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
                            self.adicionar_log("REMOVER", id_resolvido, "Ativo removido da base de dados.")
                            for c in self.campos_rem: c.texto = ""
                            self.definir_mensagem("Ativo removido com sucesso!", COR_AMBAR)
                        else:
                            self.definir_mensagem("Ativo não encontrado no sistema.", COR_VERMELHO_NEON)
                        self.sincronizar_dados()

            elif self.modal_ativo == "DASHBOARD_TELAO":
                for r_log, log_data in self.rects_logs:
                    if r_log.collidepoint(pos_mouse):
                        self.log_selecionado = log_data
                        return

            elif self.modal_ativo == "SERVIDOR_INFRA":
                for r_node, ativo in self.rects_matriz_risco:
                    if r_node.collidepoint(pos_mouse):
                        self.ativo_inspecionado_servidor = str(ativo['id'])
                        self.scroll_vuln_servidor = 0
                        abertas = [v for v in ativo.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]
                        self.vuln_selecionada_servidor = abertas[0] if abertas else None
                        if self.vuln_selecionada_servidor:
                            cve_sel = str(self.vuln_selecionada_servidor.get('cve', '')).strip().upper()
                            desc_sel = str(self.vuln_selecionada_servidor.get('descricao', '')).strip().casefold()
                            if cve_sel.startswith("CVE-") and desc_sel not in CORRECOES_SUGERIDAS_VULN and cve_sel not in self.sugestoes_nvd:
                                self.worker_nvd.solicitar(cve_sel, 0)
                        self.vuln_log.texto = ""
                        self.mensagem_status = ""
                        return

                for r_vuln, v_srv in self.rects_vulns_servidor:
                    if r_vuln.collidepoint(pos_mouse):
                        self.vuln_selecionada_servidor = v_srv
                        cve_sel = str(v_srv.get('cve', '')).strip().upper()
                        desc_sel = str(v_srv.get('descricao', '')).strip().casefold()
                        if cve_sel.startswith("CVE-") and desc_sel not in CORRECOES_SUGERIDAS_VULN and cve_sel not in self.sugestoes_nvd:
                            self.worker_nvd.solicitar(cve_sel, 0)
                        self.mensagem_status = ""
                        return

                rect_desc_srv = pygame.Rect(763, 285, 244, 184)
                if self.vuln_selecionada_servidor and rect_desc_srv.collidepoint(pos_mouse):
                    cve_sel = str(self.vuln_selecionada_servidor.get('cve', '')).strip().upper()
                    desc_sel = str(self.vuln_selecionada_servidor.get('descricao', '')).strip().casefold()
                    if cve_sel.startswith("CVE-") and desc_sel not in CORRECOES_SUGERIDAS_VULN and cve_sel not in self.sugestoes_nvd:
                        self.worker_nvd.solicitar(cve_sel, 0)
                    self.descricao_expandida = True
                    return

                rect_btn_corrigir_srv = pygame.Rect(763, 530, 244, 46)
                if rect_btn_corrigir_srv.collidepoint(pos_mouse):
                    if not self.ativo_inspecionado_servidor or not self.vuln_selecionada_servidor:
                        self.definir_mensagem("Selecione um aparelho com alerta (!) para corrigir.", COR_LARANJA)
                        return
                    log_texto = self.vuln_log.texto.strip()
                    if not log_texto:
                        self.definir_mensagem("Escreva no campo acima o que foi feito na correção.", COR_LARANJA)
                        return

                    id_alvo = str(self.ativo_inspecionado_servidor)
                    cve_alvo = self.vuln_selecionada_servidor.get('cve', '')
                    desc_alvo = self.vuln_selecionada_servidor.get('descricao', '')
                    sucesso = corrigir_vulnerabilidade(id_alvo, cve_alvo, desc_alvo)
                    if sucesso:
                        self.adicionar_log("CORREÇÃO", id_alvo, log_texto)
                        self.vuln_log.texto = ""
                        self.scroll_vuln_servidor = 0
                        self.definir_mensagem("Sucesso! Falha corrigida e risco da sala atualizado.", COR_VERDE_MATRIX)
                    else:
                        self.definir_mensagem("Não foi possível corrigir a falha selecionada.", COR_VERMELHO_NEON)
                    self.sincronizar_dados()
                    return

            elif self.modal_ativo == "VULN_PATCH":
                for r_item, d in self.rects_ativos_vuln:
                    if r_item.collidepoint(pos_mouse):
                        self.vuln_id.texto = str(d['id'])
                        self._limpar_busca_nvd()
                        self.preencher_vulnerabilidade_predefinida("")
                        self.mensagem_status = ""
                        return

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
                        cve_sel = str(v.get('cve', '')).strip().upper()
                        desc_sel = str(v.get('descricao', '')).strip().casefold()
                        if cve_sel.startswith("CVE-") and desc_sel not in CORRECOES_SUGERIDAS_VULN and cve_sel not in self.sugestoes_nvd:
                            self.worker_nvd.solicitar(cve_sel, 0)
                        self.ativo_inspecionado_servidor = str(v['id_ativo'])
                        self.scroll_vuln_servidor = 0
                        ativo_v = next((a for a in self.ativos_brutos if str(a.get('id')) == str(v['id_ativo'])), None)
                        if ativo_v:
                            sala_v = str(ativo_v.get('local', '')).strip().casefold()
                            srv_sala = next(
                                (s for s in self.ativos_brutos if s.get('tipo', '').upper() == 'SERVIDOR' and str(s.get('local', '')).strip().casefold() == sala_v),
                                None
                            )
                            if srv_sala:
                                self.servidor_foco_painel = str(srv_sala['id'])
                        self.mensagem_status = ""
                        return

                painel_desc_vuln = pygame.Rect(600, 405, 400, 163)
                if self.vuln_desc.texto.strip() and not self.vuln_modelo.menu_aberto and painel_desc_vuln.collidepoint(pos_mouse):
                    cve_sel = self.vuln_cve.texto.strip().upper()
                    desc_sel = self.vuln_desc.texto.strip().casefold()
                    if cve_sel.startswith("CVE-") and desc_sel not in CORRECOES_SUGERIDAS_VULN and cve_sel not in self.sugestoes_nvd:
                        self.worker_nvd.solicitar(cve_sel, 0)
                    self.descricao_expandida = True
                    return

                rect_btn_registrar = pygame.Rect(280, 520, 300, 48)
                
                if rect_btn_registrar.collidepoint(pos_mouse):
                    if not self.vuln_modelo.texto:
                        self.definir_mensagem("Selecione uma falha na lista de vulnerabilidades.", COR_LARANJA)
                        return

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
                        self.ativo_inspecionado_servidor = str(id_resolvido)
                        self.scroll_vuln_servidor = 0
                        for c in self.campos_vuln: c.texto = ""
                        self._limpar_busca_nvd()
                        self.vuln_sev.definir_valor("")
                        self.vuln_stat.definir_valor(Equipamento.STATUS_ABERTO)
                        self.definir_mensagem("Falha registrada! Vá ao Servidor para corrigir.", COR_VERMELHO_NEON)
                    else:
                        self.definir_mensagem("Selecione um ativo antes de registrar a falha.", COR_VERMELHO_NEON)
                    self.sincronizar_dados()

            if not pygame.Rect(250, 60, LARGURA_TELA - 500, ALTURA_TELA - 120).collidepoint(pos_mouse):
                self.modal_ativo = None
                self.descricao_expandida = False
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
        elif self.modal_ativo == "SERVIDOR_INFRA":
            campos_ativos = [self.vuln_log]

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
                    painel_ativos = pygame.Rect(600, 140, 400, 130)
                    painel_vulns = pygame.Rect(600, 280, 400, 115)
                    if painel_ativos.collidepoint(pos_mouse):
                        self.scroll_vuln_inv -= evento.y
                        max_scroll = max(0, len(self.ativos_brutos) - 4)
                        self.scroll_vuln_inv = max(0, min(self.scroll_vuln_inv, max_scroll))
                    elif painel_vulns.collidepoint(pos_mouse):
                        self.scroll_vuln_lista -= evento.y
                        max_scroll = max(0, len(self.lista_vulns_ativas) - 3)
                        self.scroll_vuln_lista = max(0, min(self.scroll_vuln_lista, max_scroll))

                elif self.modal_ativo == "SERVIDOR_INFRA":
                    area_gavetas = pygame.Rect(265, 125, 145, 465)
                    area_patch = pygame.Rect(755, 125, 260, 465)
                    if area_gavetas.collidepoint(pos_mouse):
                        self.scroll_gaveta_servidores -= evento.y
                        max_scroll = max(0, len([a for a in self.ativos_brutos if a.get('tipo', '').upper() == 'SERVIDOR']) - 9)
                        self.scroll_gaveta_servidores = max(0, min(self.scroll_gaveta_servidores, max_scroll))
                    elif area_patch.collidepoint(pos_mouse):
                        ativo_insp = next(
                            (a for a in self.ativos_brutos if str(a.get('id', '')) == str(self.ativo_inspecionado_servidor)),
                            None
                        )
                        total_v = len([v for v in ativo_insp.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]) if ativo_insp else 0
                        self.scroll_vuln_servidor -= evento.y
                        max_scroll_v = max(0, total_v - 3)
                        self.scroll_vuln_servidor = max(0, min(self.scroll_vuln_servidor, max_scroll_v))

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
                    campo in (self.cad_tipo, self.cad_loc, self.upd_loc)
                    and evento.type == pygame.MOUSEBUTTONDOWN
                    and campo.texto != texto_anterior
                ):
                    break

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                self.tratar_clique(pos_mouse)

