import datetime
import random
import pygame
from ativos import Equipamento
from interface.configuracoes import (
    LARGURA_TELA,
    ALTURA_TELA,
    COR_FUNDO,
    COR_CHAO,
    COR_GRADE,
    COR_PAREDE,
    COR_TEXTO,
    COR_TEXTO_MUTED,
    COR_CIANO_NEON,
    COR_VERDE_MATRIX,
    COR_AMBAR,
    COR_LARANJA,
    COR_VERMELHO_CLARO,
    COR_VERMELHO_ESCURO,
    COR_VERMELHO_NEON,
    COR_PAINEL,
    COR_PAINEL_BORDA,
    DESCRICOES_DIDATICAS_VULN,
    CORRECOES_SUGERIDAS_VULN
)

# ==========================================
# SUB-SESSÃO: RENDERIZAÇÃO GRÁFICA
# ==========================================
class RenderizadorGrafico:
    def desenhar_cenario(self):
        self.tela.fill(COR_FUNDO)
        pygame.draw.rect(self.tela, COR_PAREDE, (0, 0, LARGURA_TELA, 340))

        for px in range(160, LARGURA_TELA, 160):
            pygame.draw.line(self.tela, (12, 22, 36), (px, 36), (px, 340), 1)
        pygame.draw.line(self.tela, (14, 26, 42), (0, 190), (LARGURA_TELA, 190), 1)
        
        cor_drop = (95, 22, 28) if self.alerta_ativo else (0, 75, 25)
        for drop in self.bg_drops:
            drop['y'] += drop['speed']
            if drop['y'] > 340: 
                drop['y'] = random.randint(-200, -10)
                drop['x'] = random.randint(0, LARGURA_TELA)
                drop['char'] = random.choice(['0', '1', 'A', 'B', 'C', 'D', 'E', 'F', 'X'])
            txt_superficie = self.fonte_p.render(drop['char'], True, cor_drop) 
            self.tela.blit(txt_superficie, (drop['x'], drop['y']))
            
        pygame.draw.line(self.tela, (30, 45, 70), (0, 340), (LARGURA_TELA, 340), 2)
        pygame.draw.rect(self.tela, COR_CHAO, (0, 340, LARGURA_TELA, ALTURA_TELA - 340))
        for y in range(370, ALTURA_TELA, 45): pygame.draw.line(self.tela, COR_GRADE, (0, y), (LARGURA_TELA, y), 1)
        for x in range(-200, LARGURA_TELA + 300, 120): pygame.draw.line(self.tela, COR_GRADE, (x, ALTURA_TELA), (LARGURA_TELA // 2, 280), 1)

        cor_trilha = self.cor_alerta_atual if self.alerta_ativo else (0, 120, 60)
        trilhas = [
            [(235, 560), (235, 675), (580, 675), (580, 650)],
            [(740, 585), (960, 585), (960, 420), (1020, 420)],
            [(640, 290), (640, 340), (580, 470)],
            [(215, 290), (215, 340), (235, 400)]
        ]
        for pontos_trilha in trilhas:
            pygame.draw.lines(self.tela, cor_trilha, False, pontos_trilha, 2)
            for px, py in pontos_trilha:
                pygame.draw.circle(self.tela, cor_trilha, (px, py), 3)

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
        self.tela.blit(self.fonte_p.render("[ NOTEBOOK: ATIVOS ]", True, COR_CIANO_NEON), (self.rect_notebook.x + 8, self.rect_notebook.y - 20))

        cor_srv = COR_AMBAR if self.objeto_em_hover == "SERVIDOR" else (40, 60, 90)
        pygame.draw.rect(self.tela, (14, 20, 32), self.rect_servidor)
        pygame.draw.rect(self.tela, cor_srv, self.rect_servidor, 2)
        ticks = pygame.time.get_ticks()
        for i in range(7):
            r_blade = pygame.Rect(self.rect_servidor.x + 15, self.rect_servidor.y + 30 + (i * 60), 170, 48)
            pygame.draw.rect(self.tela, (22, 32, 50), r_blade)
            pygame.draw.rect(self.tela, (40, 58, 86), r_blade, 1)
            self.tela.blit(self.fonte_p.render(f"Gaveta 0{i+1}", True, COR_TEXTO_MUTED), (r_blade.x + 8, r_blade.y + 8))
            led_aceso = ((ticks // (280 + i * 85)) % 2 == 0)
            
            if self.alerta_ativo:
                cor_led = self.cor_alerta_atual if led_aceso else (80, 10, 20)
            else:
                cor_led = COR_VERDE_MATRIX if led_aceso else COR_AMBAR
                
            pygame.draw.circle(self.tela, cor_led, (r_blade.x + 150, r_blade.y + 18), 4)
            
        self.tela.blit(self.fonte_p.render("[ SERVIDOR: REDE E CORREÇÕES ]", True, COR_AMBAR), (self.rect_servidor.x - 10, self.rect_servidor.y - 22))

        piscar = self.alerta_ativo and ((ticks // 250) % 2 == 0)
        cor_pc = self.cor_alerta_atual if piscar else (COR_CIANO_NEON if self.objeto_em_hover == "WORKSTATION" else (45, 65, 95))
        fundo_tela = (80, 10, 20) if piscar else ((15, 30, 45) if self.objeto_em_hover == "WORKSTATION" else (15, 22, 35))
        rect_pc_tela = pygame.Rect(self.rect_workstation.x + 20, self.rect_workstation.y, 150, 105)
        pygame.draw.rect(self.tela, fundo_tela, rect_pc_tela)
        pygame.draw.rect(self.tela, cor_pc, rect_pc_tela, 3 if self.alerta_ativo else 2)
        pygame.draw.rect(self.tela, (30, 45, 65), (self.rect_workstation.x + 85, self.rect_workstation.y + 105, 20, 25))
        pygame.draw.rect(self.tela, (30, 45, 65), (self.rect_workstation.x + 65, self.rect_workstation.y + 125, 60, 10))
        
        rotulo_pc = self.nivel_alerta_str if self.alerta_ativo else "COMPUTADOR SEGURO"
        self.tela.blit(self.fonte_p.render(f"[ {rotulo_pc} ]", True, self.cor_alerta_atual if self.alerta_ativo else COR_VERDE_MATRIX), (self.rect_workstation.x, self.rect_workstation.y - 20))

        # =======================================================
        # 1. ALERTA DA WORKSTATION (EMOJI Bug)
        # =======================================================
        if self.alerta_ativo and piscar:
            bug_x = rect_pc_tela.centerx - 9
            bug_y = rect_pc_tela.centery - 15
            
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
        titulo_telao = "PAINEL CENTRAL: HISTÓRICO EM TEMPO REAL" if fase_telao == 0 else "PAINEL CENTRAL: FALHAS DE SEGURANÇA ATIVAS"
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
                        txt_vuln = f"> URGENTE! Ativo ID:{v['id_ativo']} ({v['nome']}) - CVE: {v['cve']} ({v['severidade'].upper()})"
                        
                        sev_log = v['severidade'].lower()
                        if sev_log == 'baixa': cor_log_v = COR_AMBAR
                        elif sev_log == 'media': cor_log_v = COR_LARANJA
                        elif sev_log == 'alta': cor_log_v = COR_VERMELHO_CLARO
                        else: cor_log_v = COR_VERMELHO_ESCURO
                        
                        self.tela.blit(self.fonte_p.render(txt_vuln, True, cor_log_v), (area_rolagem.x + 5, pos_y_atual))
                        pos_y_atual += 30
            
        self.tela.set_clip(None)

        # =======================================================
        # 3. PAINEL LATERAL ESQUERDO (MONITOR DE SALAS / REDE)
        # =======================================================
        rect_monitor_salas = pygame.Rect(65, 90, 300, 200)
        pygame.draw.rect(self.tela, (12, 18, 28), rect_monitor_salas)
        pygame.draw.rect(self.tela, (30, 48, 75), rect_monitor_salas, 2)
        self.tela.blit(self.fonte_m.render("MONITORAMENTO DAS SALAS", True, COR_AMBAR), (rect_monitor_salas.x + 14, rect_monitor_salas.y + 10))
        pygame.draw.line(self.tela, (30, 48, 75), (rect_monitor_salas.x + 10, rect_monitor_salas.y + 34), (rect_monitor_salas.right - 10, rect_monitor_salas.y + 34), 1)

        salas_painel = [
            linha for linha in self.relatorio_risco
            if linha.startswith("SALA:")
        ]
        if not salas_painel:
            self.tela.blit(self.fonte_p.render("Nenhuma sala monitorada.", True, COR_TEXTO_MUTED), (rect_monitor_salas.x + 14, rect_monitor_salas.y + 50))
        else:
            for idx_s, linha_s in enumerate(salas_painel[:5]):
                partes = linha_s.split("|")
                nome_s = partes[0].replace("SALA:", "").strip()
                if len(nome_s) > 12:
                    nome_s = nome_s[:10].rstrip() + ".."
                risco_s_txt = partes[1].replace("RISCO EFETIVO TOTAL:", "").strip() if len(partes) > 1 else "0.00"
                try:
                    risco_s_val = float(risco_s_txt)
                except ValueError:
                    risco_s_val = 0.0
                cor_s = COR_VERDE_MATRIX if risco_s_val == 0 else (COR_VERMELHO_CLARO if risco_s_val >= 20 else COR_AMBAR)
                ry_s = rect_monitor_salas.y + 44 + (idx_s * 28)
                pygame.draw.rect(self.tela, (18, 26, 40), (rect_monitor_salas.x + 12, ry_s, 276, 22))
                pygame.draw.circle(self.tela, cor_s, (rect_monitor_salas.x + 24, ry_s + 11), 4)
                txt_sala_mon = f"{nome_s:<12} | Risco: {risco_s_txt}"
                while txt_sala_mon and self.fonte_p.size(txt_sala_mon)[0] > 232:
                    txt_sala_mon = txt_sala_mon[:-1]
                self.tela.blit(self.fonte_p.render(txt_sala_mon, True, cor_s), (rect_monitor_salas.x + 36, ry_s + 3))

        # =======================================================
        # 4. BARRA SUPERIOR DE STATUS (TOP HUD BAR)
        # =======================================================
        rect_top_bar = pygame.Rect(0, 0, LARGURA_TELA, 36)
        pygame.draw.rect(self.tela, (8, 14, 24), rect_top_bar)
        cor_linha_topo = self.cor_alerta_atual if self.alerta_ativo else COR_CIANO_NEON
        pygame.draw.line(self.tela, cor_linha_topo, (0, 36), (LARGURA_TELA, 36), 2)

        hora_hud = datetime.datetime.now().strftime("%H:%M:%S")
        self.tela.blit(self.fonte_m.render("CENTRAL DE SEGURANÇA", True, COR_CIANO_NEON), (18, 9))
        resumo_hud = f"ATIVOS: {len(self.ativos_brutos)}  |  FALHAS EM ABERTO: {len(self.lista_vulns_ativas)}  |  SITUAÇÃO: {self.nivel_alerta_str}"
        img_resumo = self.fonte_p.render(resumo_hud, True, cor_linha_topo)
        self.tela.blit(img_resumo, (LARGURA_TELA // 2 - img_resumo.get_width() // 2, 11))
        img_hora = self.fonte_p.render(f"HORA: {hora_hud}", True, COR_AMBAR)
        self.tela.blit(img_hora, (LARGURA_TELA - img_hora.get_width() - 18, 11))

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
                self.tela.blit(self.fonte_m.render("DADOS DO ATIVO", True, COR_CIANO_NEON), (painel_detalhes.x + 12, painel_detalhes.y + 8))

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
                        ("Nome", ativo.get('nome', 'Não informado')),
                        ("Código ID", ativo.get('id', 'Não informado')),
                        ("Responsável", ativo.get('responsavel', 'Não informado')),
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
                        while texto_detalhe and self.fonte_p.size(texto_detalhe)[0] > painel_detalhes.width - 24:
                            texto_detalhe = texto_detalhe[:-1]
                        self.tela.blit(self.fonte_p.render(texto_detalhe, True, COR_TEXTO), (painel_detalhes.x + 12, painel_detalhes.y + 38 + indice * 25))
                    self.tela.set_clip(None)
                else:
                    self.tela.blit(self.fonte_p.render("Clique em um ativo para ver os dados.", True, COR_TEXTO_MUTED), (painel_detalhes.x + 12, painel_detalhes.y + 45))
            
            elif self.aba_crud_ativa == "CADASTRAR":
                for campo in self._campos_cadastro_ativos():
                    campo.desenhar(self.tela)
                    
                col_x = 630
                col_y = 190
                self.tela.blit(self.fonte_m.render("COMO PREENCHER", True, COR_AMBAR), (col_x, col_y))
                self.tela.blit(self.fonte_p.render("Escolha o tipo; o nome inicia automático.", True, COR_CIANO_NEON), (col_x, col_y + 32))
                self.tela.blit(self.fonte_p.render("Use 4 ou mais números no código ID.", True, COR_TEXTO_MUTED), (col_x, col_y + 54))
                self.tela.blit(self.fonte_p.render("Computadores: informe a memória RAM.", True, COR_TEXTO_MUTED), (col_x, col_y + 92))
                self.tela.blit(self.fonte_p.render("Roteador: informe S (sim) ou N (não).", True, COR_TEXTO_MUTED), (col_x, col_y + 114))
                self.tela.blit(self.fonte_p.render("Local: escolha uma sala ou crie nova.", True, COR_TEXTO_MUTED), (col_x, col_y + 150))
                
            elif self.aba_crud_ativa in ["ATUALIZAR", "REMOVER"]:
                campo_id_ativo = self.upd_id if self.aba_crud_ativa == "ATUALIZAR" else self.rem_id
                alvo_digitado = campo_id_ativo.texto.strip().casefold()
                ativo_alvo_hud = next(
                    (
                        d for d in self.ativos_brutos
                        if alvo_digitado and (
                            str(d.get('id', '')).casefold() == alvo_digitado
                            or str(d.get('nome', '')).casefold() == alvo_digitado
                        )
                    ),
                    None
                )

                if self.aba_crud_ativa == "ATUALIZAR":
                    for campo in self.campos_upd: campo.desenhar(self.tela)
                else:
                    for campo in self.campos_rem: campo.desenhar(self.tela)
                
                painel_ativos = pygame.Rect(630, 190, 360, 195)
                pygame.draw.rect(self.tela, (12, 18, 28), painel_ativos)
                pygame.draw.rect(self.tela, (30, 45, 68), painel_ativos, 2)
                self.tela.blit(self.fonte_m.render("EQUIPAMENTOS (CLIQUE OU ROLE)", True, COR_CIANO_NEON), (painel_ativos.x + 10, painel_ativos.y + 8))

                self.rects_ativos_crud = []
                ativos_visiveis = self.ativos_brutos[self.scroll_crud_ativos : self.scroll_crud_ativos + 7]
                
                for i, d in enumerate(ativos_visiveis):
                    r_item = pygame.Rect(painel_ativos.x + 10, painel_ativos.y + 33 + (i * 22), 340, 20)
                    selecionado = bool(ativo_alvo_hud and str(ativo_alvo_hud.get('id')) == str(d.get('id')))
                    cor_fundo_item = (10, 60, 20) if selecionado else (25, 35, 50)
                    cor_borda_item = COR_VERDE_MATRIX if selecionado else (40, 58, 85)
                    pygame.draw.rect(self.tela, cor_fundo_item, r_item)
                    pygame.draw.rect(self.tela, cor_borda_item, r_item, 1)
                    txt = f"ID: {d['id']} | {d.get('nome', '')} | {d.get('local', '')}"
                    while txt and self.fonte_p.size(txt)[0] > r_item.width - 16:
                        txt = txt[:-1]
                    self.tela.blit(self.fonte_p.render(txt, True, COR_TEXTO), (r_item.x + 10, r_item.y + 3))
                    self.rects_ativos_crud.append((r_item, d))

                painel_previa = pygame.Rect(630, 392, 360, 66)
                pygame.draw.rect(self.tela, (8, 12, 18), painel_previa)
                pygame.draw.rect(self.tela, COR_AMBAR if ativo_alvo_hud else (40, 58, 85), painel_previa, 1)
                if ativo_alvo_hud:
                    resp_atual = ativo_alvo_hud.get('responsavel', 'N/A')
                    loc_atual = ativo_alvo_hud.get('local', 'N/A')
                    if self.aba_crud_ativa == "ATUALIZAR":
                        novo_r = self.upd_resp.texto.strip().title() or resp_atual
                        novo_l = self.upd_loc.texto.strip() or loc_atual
                        lin_p1 = f"SELECIONADO: {ativo_alvo_hud.get('nome', '').upper()} ({ativo_alvo_hud.get('tipo', '')})"
                        lin_p2 = f"Resp.: {resp_atual[:14]} -> {novo_r[:14]}"
                        lin_p3 = f"Local: {loc_atual[:14]} -> {novo_l[:14]}"
                        while lin_p1 and self.fonte_p.size(lin_p1)[0] > painel_previa.width - 20:
                            lin_p1 = lin_p1[:-1]
                        self.tela.blit(self.fonte_p.render(lin_p1, True, COR_AMBAR), (painel_previa.x + 10, painel_previa.y + 6))
                        self.tela.blit(self.fonte_p.render(lin_p2, True, COR_TEXTO), (painel_previa.x + 10, painel_previa.y + 25))
                        self.tela.blit(self.fonte_p.render(lin_p3, True, COR_TEXTO), (painel_previa.x + 10, painel_previa.y + 44))
                    else:
                        lin_r1 = f"REMOVER: {ativo_alvo_hud.get('nome', '').upper()} (ID {ativo_alvo_hud.get('id')})"
                        lin_r2 = f"Resp.: {resp_atual[:14]} | Local: {loc_atual[:14]}"
                        while lin_r1 and self.fonte_p.size(lin_r1)[0] > painel_previa.width - 20:
                            lin_r1 = lin_r1[:-1]
                        self.tela.blit(self.fonte_p.render(lin_r1, True, COR_VERMELHO_CLARO), (painel_previa.x + 10, painel_previa.y + 8))
                        self.tela.blit(self.fonte_p.render(lin_r2, True, COR_TEXTO_MUTED), (painel_previa.x + 10, painel_previa.y + 32))
                else:
                    self.tela.blit(self.fonte_p.render("Clique em um ativo na lista acima ou", True, COR_TEXTO_MUTED), (painel_previa.x + 10, painel_previa.y + 14))
                    self.tela.blit(self.fonte_p.render("digite o ID ou Nome para selecionar.", True, COR_TEXTO_MUTED), (painel_previa.x + 10, painel_previa.y + 34))

            if self.mensagem_status:
                msg_crud = self.mensagem_status
                while msg_crud and self.fonte_m.size(msg_crud)[0] > rect_modal.width - 90:
                    msg_crud = msg_crud[:-1]
                self.tela.blit(self.fonte_m.render(msg_crud, True, self.cor_status), (320, 490))

            if self.aba_crud_ativa != "LISTAR":
                btn_exec = pygame.Rect(320, 520, 340, 44)
                pygame.draw.rect(self.tela, (20, 45, 60), btn_exec)
                pygame.draw.rect(self.tela, COR_CIANO_NEON, btn_exec, 1)
                self.tela.blit(self.fonte_m.render(f"CONFIRMAR: {self.aba_crud_ativa}", True, COR_CIANO_NEON), (btn_exec.x + 20, btn_exec.y + 12))

            if self.aba_crud_ativa == "CADASTRAR":
                self.cad_tipo.desenhar_menu(self.tela)
                if self.cad_loc.texto != "__NOVA_SALA__":
                    self.cad_loc.desenhar_menu(self.tela)
            elif self.aba_crud_ativa == "ATUALIZAR":
                self.upd_loc.desenhar_menu(self.tela)

        elif self.modal_ativo == "DASHBOARD_TELAO":
            self.tela.blit(self.fonte_g.render("PAINEL DE REGISTROS E ATIVIDADES", True, COR_CIANO_NEON), (rect_modal.x + 30, rect_modal.y + 24))
            
            corpo = pygame.Rect(rect_modal.x + 30, rect_modal.y + 70, rect_modal.width - 60, 390)
            pygame.draw.rect(self.tela, (12, 18, 28), corpo)
            pygame.draw.rect(self.tela, (30, 45, 68), corpo, 1)
            
            area_logs = pygame.Rect(corpo.x + 10, corpo.y + 10, 380, 370)
            pygame.draw.rect(self.tela, (8, 12, 18), area_logs)
            pygame.draw.rect(self.tela, (40, 58, 85), area_logs, 1)
            self.tela.blit(self.fonte_p.render("HISTÓRICO DE AÇÕES (Role o mouse):", True, COR_AMBAR), (area_logs.x + 10, area_logs.y + 10))

            self.rects_logs = []
            logs_visiveis = self.historico_logs[self.scroll_logs:self.scroll_logs + 12]
            for i, log in enumerate(logs_visiveis):
                r_log = pygame.Rect(area_logs.x + 10, area_logs.y + 35 + (i * 26), 360, 24)
                cor_fundo_log = (20, 35, 50) if self.log_selecionado == log else (15, 20, 30)
                pygame.draw.rect(self.tela, cor_fundo_log, r_log)
                pygame.draw.rect(self.tela, (30, 45, 60), r_log, 1)
                txt_log = f"[{log['hora']}] {log['acao']} - Ativo: {log['alvo']}"
                while txt_log and self.fonte_p.size(txt_log)[0] > r_log.width - 16:
                    txt_log = txt_log[:-1]
                
                cor_log_txt = COR_TEXTO
                if log['acao'] == "CORREÇÃO": cor_log_txt = COR_VERDE_MATRIX
                elif log['acao'] == "INCIDENTE": cor_log_txt = COR_VERMELHO_NEON
                elif log['acao'] == "REMOVER": cor_log_txt = COR_AMBAR
                
                self.tela.blit(self.fonte_p.render(txt_log, True, cor_log_txt), (r_log.x + 8, r_log.y + 4))
                self.rects_logs.append((r_log, log))

            area_detalhe = pygame.Rect(corpo.x + 400, corpo.y + 10, 300, 370)
            pygame.draw.rect(self.tela, (10, 15, 22), area_detalhe)
            pygame.draw.rect(self.tela, COR_CIANO_NEON, area_detalhe, 1)
            self.tela.set_clip(area_detalhe.inflate(-6, -6))
            self.tela.blit(self.fonte_m.render("DETALHES DO REGISTRO", True, COR_CIANO_NEON), (area_detalhe.x + 10, area_detalhe.y + 10))
            
            if self.log_selecionado:
                self.tela.blit(self.fonte_p.render(f"Ação: {self.log_selecionado['acao']}", True, COR_TEXTO_MUTED), (area_detalhe.x + 10, area_detalhe.y + 40))
                self.tela.blit(self.fonte_p.render(f"Hora: {self.log_selecionado['hora']}", True, COR_TEXTO_MUTED), (area_detalhe.x + 10, area_detalhe.y + 60))
                txt_alvo_log = f"Ativo: {self.log_selecionado['alvo']}"
                while txt_alvo_log and self.fonte_p.size(txt_alvo_log)[0] > area_detalhe.width - 20:
                    txt_alvo_log = txt_alvo_log[:-1]
                self.tela.blit(self.fonte_p.render(txt_alvo_log, True, COR_TEXTO_MUTED), (area_detalhe.x + 10, area_detalhe.y + 80))
                
                palavras = self.log_selecionado['detalhes'].split(' ')
                linhas = []
                linha_atual = ""
                for p in palavras:
                    teste_l = (linha_atual + " " + p).strip()
                    if self.fonte_p.size(teste_l)[0] <= area_detalhe.width - 20:
                        linha_atual = teste_l
                    else:
                        if linha_atual:
                            linhas.append(linha_atual)
                        linha_atual = p
                if linha_atual:
                    linhas.append(linha_atual)
                
                self.tela.blit(self.fonte_p.render("Descrição da ação:", True, COR_AMBAR), (area_detalhe.x + 10, area_detalhe.y + 110))
                for idx, l in enumerate(linhas[:11]):
                    while l and self.fonte_p.size(l)[0] > area_detalhe.width - 20:
                        l = l[:-1]
                    self.tela.blit(self.fonte_p.render(l, True, COR_TEXTO), (area_detalhe.x + 10, area_detalhe.y + 130 + (idx * 20)))
            else:
                self.tela.blit(self.fonte_p.render("Clique em um registro ao lado", True, (60, 80, 100)), (area_detalhe.x + 10, area_detalhe.y + 120))
                self.tela.blit(self.fonte_p.render("para ver todos os detalhes.", True, (60, 80, 100)), (area_detalhe.x + 10, area_detalhe.y + 140))
            self.tela.set_clip(None)

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
            titulo_risco = f"RISCO DA SALA {sala_focada or '—'} | TOTAL DA REDE: {risco_global_total}"
            while titulo_risco and self.fonte_g.size(titulo_risco)[0] > rect_modal.width - 80:
                titulo_risco = titulo_risco[:-1]
            self.tela.blit(self.fonte_g.render(titulo_risco, True, COR_AMBAR), (rect_modal.x + 20, rect_modal.y + 24))
            
            area_gavetas = pygame.Rect(265, 125, 145, 465)
            area_arvore = pygame.Rect(420, 125, 325, 465)
            area_patch = pygame.Rect(755, 125, 260, 465)
            
            pygame.draw.rect(self.tela, (12, 18, 28), area_gavetas)
            pygame.draw.rect(self.tela, (30, 45, 68), area_gavetas, 1)
            self.tela.blit(self.fonte_m.render("SERVIDORES", True, COR_CIANO_NEON), (area_gavetas.x + 10, area_gavetas.y + 10))

            pygame.draw.rect(self.tela, (10, 15, 20), area_arvore)
            pygame.draw.rect(self.tela, COR_AMBAR, area_arvore, 1)

            pygame.draw.rect(self.tela, (12, 18, 28), area_patch)
            pygame.draw.rect(self.tela, COR_CIANO_NEON, area_patch, 1)
            self.tela.blit(self.fonte_m.render("CORREÇÃO DE FALHAS", True, COR_CIANO_NEON), (area_patch.x + 10, area_patch.y + 8))

            self.rects_matriz_risco = []

            def obter_risco_efetivo(nome_busca):
                for linha in self.relatorio_risco:
                    if f"[{nome_busca.lower()}" in linha.lower():
                        try: return linha.split("Risco Efetivo:")[-1].strip()
                        except: pass
                return "0.00"

            def desenhar_icone_ativo(x, y, ativo, modo_compacto=False):
                tipo = ativo.get('tipo', '').upper()
                nome = ativo.get('nome', 'UNK').upper()
                risco_efetivo = obter_risco_efetivo(nome)
                
                vulns_abertas = [v for v in ativo.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]
                tem_alerta = len(vulns_abertas) > 0
                try:
                    ameacado = float(risco_efetivo) > 0.0
                except ValueError:
                    ameacado = False
                
                if tem_alerta or ameacado:
                    pesos = {'baixa': 1, 'media': 2, 'alta': 3, 'critica': 4}
                    vulns_referencia = vulns_abertas if tem_alerta else [
                        v for a in self.ativos_brutos
                        if str(a.get('local', '')).strip().casefold() == str(ativo.get('local', '')).strip().casefold()
                        for v in a.get('vulnerabilidades', [])
                        if Equipamento.vulnerabilidade_esta_aberta(v)
                    ]
                    max_sev = max([pesos.get(v.get('severidade', 'baixa').lower(), 1) for v in vulns_referencia], default=1)
                    if tem_alerta:
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
                
                rect_clique = pygame.Rect(x - 30, y - 50, 60, 100) if tipo == "SERVIDOR" else pygame.Rect(x - 35, y - 35, 70, 70)
                if rect_clique.collidepoint(pos_mouse):
                    cor_fundo = (80, 20, 20) if (tem_alerta or ameacado) else (30, 45, 65)

                if str(ativo.get('id')) == str(self.ativo_inspecionado_servidor):
                    pygame.draw.rect(self.tela, COR_CIANO_NEON, rect_clique.inflate(6, 6), 1, border_radius=8)

                if tipo == "SERVIDOR":
                    rect_vis = pygame.Rect(x - 30, y - 50, 60, 100)
                    pygame.draw.rect(self.tela, cor_fundo, rect_vis, border_radius=6)
                    pygame.draw.rect(self.tela, cor_borda, rect_vis, 2, border_radius=6)
                    for j in range(3):
                        pygame.draw.line(self.tela, cor_borda, (x - 20, y - 20 + j*20), (x + 20, y - 20 + j*20), 2)
                        
                elif tipo == "DESKTOP":
                    monitor = pygame.Rect(x - 30, y - 22, 60, 36)
                    pygame.draw.rect(self.tela, cor_fundo, monitor, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, monitor, 2, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, (x - 7, y + 14, 14, 9)) 
                    pygame.draw.line(self.tela, cor_borda, (x - 18, y + 23), (x + 18, y + 23), 3) 
                    
                elif tipo == "NOTEBOOK":
                    tela_nb = pygame.Rect(x - 26, y - 18, 52, 32)
                    pygame.draw.rect(self.tela, cor_fundo, tela_nb, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, tela_nb, 2, border_radius=4)
                    base_nb = pygame.Rect(x - 30, y + 14, 60, 7)
                    pygame.draw.rect(self.tela, cor_fundo, base_nb, border_radius=2)
                    pygame.draw.rect(self.tela, cor_borda, base_nb, 2, border_radius=2)
                    
                elif tipo == "ROTEADOR":
                    rot_box = pygame.Rect(x - 30, y - 5, 60, 14)
                    pygame.draw.rect(self.tela, cor_fundo, rot_box, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, rot_box, 2, border_radius=4)
                    pygame.draw.line(self.tela, cor_borda, (x - 18, y - 5), (x - 22, y - 22), 2) 
                    pygame.draw.line(self.tela, cor_borda, (x + 18, y - 5), (x + 22, y - 22), 2) 
                    
                else:
                    rect_vis = pygame.Rect(x - 28, y - 18, 56, 36)
                    pygame.draw.rect(self.tela, cor_fundo, rect_vis, border_radius=4)
                    pygame.draw.rect(self.tela, cor_borda, rect_vis, 2, border_radius=4)

                nome_lbl = self.fonte_p.render(nome[:8] if modo_compacto else nome[:10], True, COR_TEXTO)
                txt_risco_no = f"R:{risco_efetivo}" if modo_compacto else f"Risco: {risco_efetivo}"
                risco_lbl = self.fonte_p.render(txt_risco_no, True, cor_borda)
                txt_sev_no = severidade_principal if (tem_alerta and modo_compacto) else (f"Nível: {severidade_principal}" if tem_alerta else "")
                severidade_lbl = self.fonte_p.render(txt_sev_no, True, cor_borda)
                
                offset_y_nome = -68 if tipo == "SERVIDOR" else -42
                offset_y_risco = 54 if tipo == "SERVIDOR" else 30
                
                pos_nome = (int(x - nome_lbl.get_width() // 2), int(y + offset_y_nome))
                pos_risco = (int(x - risco_lbl.get_width() // 2), int(y + offset_y_risco))
                pygame.draw.rect(self.tela, (10, 15, 20), (pos_nome[0] - 2, pos_nome[1], nome_lbl.get_width() + 4, nome_lbl.get_height()))
                self.tela.blit(nome_lbl, pos_nome)
                pygame.draw.rect(self.tela, (10, 15, 20), (pos_risco[0] - 2, pos_risco[1], risco_lbl.get_width() + 4, risco_lbl.get_height()))
                self.tela.blit(risco_lbl, pos_risco)
                if tem_alerta:
                    pos_sev = (int(x - severidade_lbl.get_width() // 2), int(y + offset_y_risco + 15))
                    pygame.draw.rect(self.tela, (10, 15, 20), (pos_sev[0] - 2, pos_sev[1], severidade_lbl.get_width() + 4, severidade_lbl.get_height()))
                    self.tela.blit(severidade_lbl, pos_sev)

                if tem_alerta:
                    pygame.draw.circle(self.tela, (0,0,0), (int(x + 26), int(y - 26)), 11)
                    pygame.draw.circle(self.tela, cor_borda, (int(x + 26), int(y - 26)), 11, 2)
                    exc = self.fonte_m.render("!", True, cor_borda)
                    self.tela.blit(exc, (int(x + 22), int(y - 34)))

                self.rects_matriz_risco.append((rect_clique, ativo))

            servidores = [a for a in self.ativos_brutos if a.get('tipo', '').upper() == 'SERVIDOR']
            
            if not self.servidor_foco_painel and servidores:
                self.servidor_foco_painel = str(servidores[0]['id'])
            
            servidores_visiveis = servidores[self.scroll_gaveta_servidores : self.scroll_gaveta_servidores + 9]
            
            for i, srv in enumerate(servidores_visiveis):
                r_gaveta = pygame.Rect(area_gavetas.x + 8, area_gavetas.y + 40 + (i * 45), 129, 35)
                
                esta_aberta = (self.servidor_foco_painel == str(srv['id']))
                cor_fundo = (30, 60, 90) if esta_aberta else (20, 30, 45)
                
                pygame.draw.rect(self.tela, cor_fundo, r_gaveta, border_radius=4)
                pygame.draw.rect(self.tela, COR_CIANO_NEON if esta_aberta else (40, 58, 85), r_gaveta, 1, border_radius=4)
                
                txt_srv = f"{srv.get('nome', '')} (ID {srv['id']})"
                while txt_srv and self.fonte_p.size(txt_srv)[0] > r_gaveta.width - 12:
                    txt_srv = txt_srv[:-1]
                self.tela.blit(self.fonte_p.render(txt_srv, True, COR_TEXTO), (r_gaveta.x + 6, r_gaveta.y + 10))
                
                if r_gaveta.collidepoint(pos_mouse) and pygame.mouse.get_pressed()[0]:
                    if self.servidor_foco_painel != str(srv['id']):
                        self.servidor_foco_painel = str(srv['id'])
                        self.ativo_inspecionado_servidor = str(srv['id'])
                        self.scroll_vuln_servidor = 0
                        abertas_srv = [v for v in srv.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]
                        self.vuln_selecionada_servidor = abertas_srv[0] if abertas_srv else None
                        self.vuln_log.texto = ""
                        self.descricao_expandida = False

            self.tela.set_clip(area_arvore.inflate(-4, -4))
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
                    ids_sala = {str(a.get('id')) for a in ativos_da_sala}
                    if str(self.ativo_inspecionado_servidor) not in ids_sala:
                        self.ativo_inspecionado_servidor = str(srv_alvo['id'])
                        self.scroll_vuln_servidor = 0
                        abertas_ini = [v for v in srv_alvo.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]
                        self.vuln_selecionada_servidor = abertas_ini[0] if abertas_ini else None

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
                        compacto_end = len(endpoints) >= 3
                        for i, end in enumerate(endpoints):
                            ex = area_arvore.x + espaco_end * (i + 1)
                            
                            if pos_roteadores:
                                idx_rot = i % len(pos_roteadores)
                                rx_pai = pos_roteadores[idx_rot][0]
                                pygame.draw.line(self.tela, (40, 70, 90), (rx_pai, y_rot + 15), (ex, y_end - 25), 2)
                            else:
                                pygame.draw.line(self.tela, (40, 70, 90), (cx_srv, y_srv + 50), (ex, y_end - 25), 2)
                                
                            desenhar_icone_ativo(ex, y_end, end, modo_compacto=compacto_end)

                    compacto_rot = len(pos_roteadores) >= 3
                    for rx, ry, rot in pos_roteadores:
                        desenhar_icone_ativo(rx, ry, rot, modo_compacto=compacto_rot)
                        
                    desenhar_icone_ativo(cx_srv, y_srv, srv_alvo, modo_compacto=False)
            else:
                self.tela.blit(self.fonte_p.render("<- Selecione um servidor.", True, COR_TEXTO_MUTED), (area_arvore.x + 20, area_arvore.y + 40))
            self.tela.set_clip(None)

            self.rects_vulns_servidor = []
            ativo_insp = next(
                (a for a in self.ativos_brutos if str(a.get('id', '')) == str(self.ativo_inspecionado_servidor)),
                None
            )
            if ativo_insp:
                nome_insp = ativo_insp.get('nome', 'UNK').upper()
                risco_insp = obter_risco_efetivo(nome_insp)
                resumo_no = f"Ativo: {nome_insp} | Risco: {risco_insp}"
                while resumo_no and self.fonte_p.size(resumo_no)[0] > area_patch.width - 16:
                    resumo_no = resumo_no[:-1]
                self.tela.blit(self.fonte_p.render(resumo_no, True, COR_AMBAR), (area_patch.x + 8, area_patch.y + 30))

                vulns_no = [v for v in ativo_insp.get('vulnerabilidades', []) if Equipamento.vulnerabilidade_esta_aberta(v)]
                rect_lista_srv = pygame.Rect(area_patch.x + 8, area_patch.y + 50, 244, 104)
                pygame.draw.rect(self.tela, (8, 12, 18), rect_lista_srv)
                pygame.draw.rect(self.tela, (45, 15, 20) if vulns_no else (25, 45, 35), rect_lista_srv, 1)
                self.tela.set_clip(rect_lista_srv.inflate(-4, -4))

                total_v_no = len(vulns_no)
                max_scroll_no = max(0, total_v_no - 3)
                if self.scroll_vuln_servidor > max_scroll_no:
                    self.scroll_vuln_servidor = max_scroll_no

                titulo_falhas = "FALHAS DO ATIVO (Role):" if total_v_no > 3 else "FALHAS DO ATIVO:"
                self.tela.blit(self.fonte_p.render(titulo_falhas, True, COR_TEXTO_MUTED), (rect_lista_srv.x + 6, rect_lista_srv.y + 5))

                if vulns_no:
                    if self.vuln_selecionada_servidor not in vulns_no:
                        self.vuln_selecionada_servidor = vulns_no[0]
                    vulns_no_visiveis = vulns_no[self.scroll_vuln_servidor : self.scroll_vuln_servidor + 3]
                    largura_item_v = 224 if total_v_no > 3 else 232
                    for idx_v, v_item in enumerate(vulns_no_visiveis):
                        r_v = pygame.Rect(rect_lista_srv.x + 6, rect_lista_srv.y + 24 + (idx_v * 25), largura_item_v, 22)
                        sev_v = v_item.get('severidade', 'baixa').lower()
                        if sev_v == 'baixa': cor_v = COR_AMBAR
                        elif sev_v == 'media': cor_v = COR_LARANJA
                        elif sev_v == 'alta': cor_v = COR_VERMELHO_CLARO
                        else: cor_v = COR_VERMELHO_ESCURO

                        selecionada_v = (self.vuln_selecionada_servidor == v_item)
                        pygame.draw.rect(self.tela, (45, 15, 20) if selecionada_v else (22, 10, 14), r_v)
                        pygame.draw.rect(self.tela, cor_v if selecionada_v else (60, 20, 30), r_v, 2 if selecionada_v else 1)
                        nome_v_curto = str(v_item.get('descricao', '')).strip()
                        if len(nome_v_curto) > 15:
                            nome_v_curto = nome_v_curto[:13].rstrip() + ".."
                        lbl_v = f"{nome_v_curto} ({v_item.get('cve', 'N/A')})"
                        while lbl_v and self.fonte_p.size(lbl_v)[0] > r_v.width - 12:
                            lbl_v = lbl_v[:-1]
                        self.tela.blit(self.fonte_p.render(lbl_v, True, cor_v), (r_v.x + 5, r_v.y + 3))
                        self.rects_vulns_servidor.append((r_v, v_item))

                    if total_v_no > 3:
                        trilho_x = rect_lista_srv.right - 8
                        trilho_y = rect_lista_srv.y + 24
                        trilho_h = 72
                        pygame.draw.rect(self.tela, (20, 28, 40), (trilho_x, trilho_y, 4, trilho_h))
                        thumb_h = max(16, int(trilho_h * (3 / total_v_no)))
                        thumb_y = trilho_y + int((trilho_h - thumb_h) * (self.scroll_vuln_servidor / max_scroll_no))
                        pygame.draw.rect(self.tela, COR_CIANO_NEON, (trilho_x, thumb_y, 4, thumb_h))
                else:
                    try:
                        herdado = float(risco_insp) > 0.0
                    except ValueError:
                        herdado = False
                    if herdado:
                        self.tela.blit(self.fonte_p.render("Sem falha direta aqui.", True, COR_AMBAR), (rect_lista_srv.x + 6, rect_lista_srv.y + 32))
                        self.tela.blit(self.fonte_p.render("Clique no ícone com '!'.", True, COR_TEXTO_MUTED), (rect_lista_srv.x + 6, rect_lista_srv.y + 52))
                    else:
                        self.tela.blit(self.fonte_p.render("EQUIPAMENTO SEGURO:", True, COR_VERDE_MATRIX), (rect_lista_srv.x + 6, rect_lista_srv.y + 32))
                        self.tela.blit(self.fonte_p.render("Nenhuma falha neste ativo.", True, COR_TEXTO_MUTED), (rect_lista_srv.x + 6, rect_lista_srv.y + 52))
                self.tela.set_clip(None)

                rect_desc_srv = pygame.Rect(area_patch.x + 8, area_patch.y + 160, 244, 184)
                hover_desc_srv = bool(self.vuln_selecionada_servidor and rect_desc_srv.collidepoint(pos_mouse) and not self.descricao_expandida)
                pygame.draw.rect(self.tela, (10, 18, 28) if hover_desc_srv else (6, 10, 16), rect_desc_srv)
                pygame.draw.rect(self.tela, COR_CIANO_NEON if hover_desc_srv else (35, 55, 80), rect_desc_srv, 1)
                self.tela.set_clip(rect_desc_srv.inflate(-4, -4))
                self.tela.blit(self.fonte_p.render("SOBRE A FALHA:", True, COR_CIANO_NEON), (rect_desc_srv.x + 8, rect_desc_srv.y + 6))

                if self.vuln_selecionada_servidor:
                    v_foco = self.vuln_selecionada_servidor
                    sev_foco = v_foco.get('severidade', 'baixa').lower()
                    if sev_foco == 'baixa': cor_foco = COR_AMBAR
                    elif sev_foco == 'media': cor_foco = COR_LARANJA
                    elif sev_foco == 'alta': cor_foco = COR_VERMELHO_CLARO
                    else: cor_foco = COR_VERMELHO_ESCURO

                    nome_foco_curto = str(v_foco.get('descricao', '')).strip()
                    if len(nome_foco_curto) > 18:
                        nome_foco_curto = nome_foco_curto[:16].rstrip() + "..."
                    meta_txt = f"{nome_foco_curto} ({sev_foco.upper()})"
                    while meta_txt and self.fonte_p.size(meta_txt)[0] > rect_desc_srv.width - 16:
                        meta_txt = meta_txt[:-1]
                    self.tela.blit(self.fonte_p.render(meta_txt, True, cor_foco), (rect_desc_srv.x + 8, rect_desc_srv.y + 24))

                    desc_chave = str(v_foco.get('descricao', '')).strip()
                    texto_didatico = DESCRICOES_DIDATICAS_VULN.get(desc_chave.casefold(), desc_chave)

                    palavras_d = texto_didatico.split(' ')
                    linhas_d = []
                    linha_at = ""
                    for p in palavras_d:
                        teste = (linha_at + " " + p).strip()
                        if self.fonte_p.size(teste)[0] <= rect_desc_srv.width - 16:
                            linha_at = teste
                        else:
                            if linha_at:
                                linhas_d.append(linha_at)
                            linha_at = p
                    if linha_at:
                        linhas_d.append(linha_at)

                    linhas_resumo = linhas_d[:4]
                    if len(linhas_d) > 4 and len(linhas_resumo[-1]) > 3:
                        linhas_resumo[-1] = linhas_resumo[-1][:-3].rstrip() + "..."
                    for idx_l, l_txt in enumerate(linhas_resumo):
                        self.tela.blit(self.fonte_p.render(l_txt, True, COR_TEXTO), (rect_desc_srv.x + 8, rect_desc_srv.y + 44 + (idx_l * 18)))

                    self.tela.blit(self.fonte_p.render("Clique p/ ler tudo e corrigir:", True, COR_VERDE_MATRIX), (rect_desc_srv.x + 8, rect_desc_srv.y + 122))
                    rect_btn_ver_srv = pygame.Rect(rect_desc_srv.x + 8, rect_desc_srv.bottom - 34, rect_desc_srv.width - 16, 26)
                    pygame.draw.rect(self.tela, (18, 42, 60) if hover_desc_srv else (12, 26, 40), rect_btn_ver_srv, border_radius=4)
                    pygame.draw.rect(self.tela, COR_CIANO_NEON, rect_btn_ver_srv, 1, border_radius=4)
                    txt_btn_srv = self.fonte_p.render("+ VER FALHA E CORREÇÃO", True, COR_CIANO_NEON)
                    self.tela.blit(txt_btn_srv, (rect_btn_ver_srv.centerx - txt_btn_srv.get_width() // 2, rect_btn_ver_srv.y + 4))
                else:
                    msg_vazia = "Clique em um equipamento com alerta (!) no mapa ao lado para entender o problema e aplicar a correção."
                    palavras_v = msg_vazia.split(' ')
                    linhas_v = []
                    linha_at = ""
                    for p in palavras_v:
                        teste = (linha_at + " " + p).strip()
                        if self.fonte_p.size(teste)[0] <= rect_desc_srv.width - 16:
                            linha_at = teste
                        else:
                            if linha_at:
                                linhas_v.append(linha_at)
                            linha_at = p
                    if linha_at:
                        linhas_v.append(linha_at)
                    for idx_l, l_txt in enumerate(linhas_v):
                        self.tela.blit(self.fonte_p.render(l_txt, True, COR_TEXTO_MUTED), (rect_desc_srv.x + 8, rect_desc_srv.y + 34 + (idx_l * 18)))
                self.tela.set_clip(None)

                self.vuln_log.desenhar(self.tela)

                btn_fix_srv = pygame.Rect(763, 530, 244, 46)
                pode_corrigir = bool(self.vuln_selecionada_servidor and self.vuln_log.texto.strip())
                cor_fundo_fix = (0, 45, 15) if pode_corrigir else (18, 24, 30)
                cor_borda_fix = COR_VERDE_MATRIX if pode_corrigir else (50, 70, 90)
                cor_texto_fix = COR_TEXTO if pode_corrigir else (90, 115, 140)
                pygame.draw.rect(self.tela, cor_fundo_fix, btn_fix_srv)
                pygame.draw.rect(self.tela, cor_borda_fix, btn_fix_srv, 2)
                self.tela.blit(self.fonte_m.render("CORRIGIR FALHA", True, cor_texto_fix), (btn_fix_srv.x + 54, btn_fix_srv.y + 14))

            if self.mensagem_status:
                msg_srv = self.mensagem_status
                while msg_srv and self.fonte_m.size(msg_srv)[0] > rect_modal.width - 40:
                    msg_srv = msg_srv[:-1]
                self.tela.blit(self.fonte_m.render(msg_srv, True, self.cor_status), (rect_modal.x + 20, rect_modal.y + 542))

        elif self.modal_ativo == "VULN_PATCH":
            self.tela.blit(self.fonte_g.render("CENTRAL DE VULNERABILIDADES", True, COR_VERMELHO_NEON), (rect_modal.x + 30, rect_modal.y + 24))
            self.tela.blit(self.fonte_p.render("CADASTRE NOVAS FALHAS OU CONSULTE OS DETALHES ABAIXO:", True, COR_TEXTO_MUTED), (rect_modal.x + 30, rect_modal.y + 58))
            
            for campo in self.campos_vuln: campo.desenhar(self.tela)
            
            painel_ativos = pygame.Rect(600, 140, 400, 130)
            pygame.draw.rect(self.tela, (12, 18, 28), painel_ativos)
            pygame.draw.rect(self.tela, (30, 45, 68), painel_ativos, 2)
            self.tela.blit(self.fonte_m.render("EQUIPAMENTOS (CLIQUE OU ROLE O MOUSE)", True, COR_CIANO_NEON), (painel_ativos.x + 10, painel_ativos.y + 8))

            self.rects_ativos_vuln = []
            inv_visiveis = self.ativos_brutos[self.scroll_vuln_inv : self.scroll_vuln_inv + 4]
            for i, d in enumerate(inv_visiveis):
                r_item = pygame.Rect(painel_ativos.x + 10, painel_ativos.y + 32 + (i * 23), 380, 20)
                selecionado = (self.vuln_id.texto.strip() == str(d.get('id', '')))
                cor_fundo_item = (10, 60, 20) if selecionado else (25, 35, 50)
                cor_borda_item = COR_VERDE_MATRIX if selecionado else (40, 58, 85)
                pygame.draw.rect(self.tela, cor_fundo_item, r_item)
                pygame.draw.rect(self.tela, cor_borda_item, r_item, 1)
                txt = f"ID: {d['id']} | {d.get('nome', '')} | {d.get('tipo', '')}"
                while txt and self.fonte_p.size(txt)[0] > r_item.width - 16:
                    txt = txt[:-1]
                self.tela.blit(self.fonte_p.render(txt, True, COR_TEXTO), (r_item.x + 10, r_item.y + 3))
                self.rects_ativos_vuln.append((r_item, d))
            
            painel_vulns = pygame.Rect(600, 280, 400, 115)
            pygame.draw.rect(self.tela, (12, 18, 28), painel_vulns)
            pygame.draw.rect(self.tela, (40, 10, 15) if self.lista_vulns_ativas else (10, 40, 20), painel_vulns, 2)
            self.tela.blit(self.fonte_m.render("FALHAS EM ABERTO (CLIQUE PARA VER)", True, COR_AMBAR), (painel_vulns.x + 10, painel_vulns.y + 8))
            
            self.rects_vulns = []
            if not self.lista_vulns_ativas:
                self.tela.blit(self.fonte_p.render("SISTEMA SEGURO: Nenhuma falha detectada.", True, COR_VERDE_MATRIX), (painel_vulns.x + 10, painel_vulns.y + 42))
            else:
                vulns_visiveis = self.lista_vulns_ativas[self.scroll_vuln_lista : self.scroll_vuln_lista + 3]
                for i, v in enumerate(vulns_visiveis):
                    r_item = pygame.Rect(painel_vulns.x + 10, painel_vulns.y + 32 + (i * 25), 380, 21)
                    
                    sev_list = v['severidade'].lower()
                    if sev_list == 'baixa': cor_txt = COR_AMBAR
                    elif sev_list == 'media': cor_txt = COR_LARANJA
                    elif sev_list == 'alta': cor_txt = COR_VERMELHO_CLARO
                    else: cor_txt = COR_VERMELHO_ESCURO

                    vuln_selecionada = (
                        self.vuln_id.texto.strip() == str(v['id_ativo'])
                        and self.vuln_cve.texto.strip().upper() == str(v['cve']).strip().upper()
                        and self.vuln_desc.texto.strip() == str(v['descricao']).strip()
                    )
                    cor_fundo_vuln = (50, 18, 25) if vuln_selecionada else (25, 10, 15)
                    cor_borda_vuln = cor_txt if vuln_selecionada else (60, 20, 30)
                    espessura_borda = 2 if vuln_selecionada else 1
                    pygame.draw.rect(self.tela, cor_fundo_vuln, r_item)
                    pygame.draw.rect(self.tela, cor_borda_vuln, r_item, espessura_borda)
                    
                    desc_item_curta = str(v['descricao']).strip()
                    if len(desc_item_curta) > 20:
                        desc_item_curta = desc_item_curta[:18].rstrip() + "..."
                    texto_vuln = f"ID:{v['id_ativo']} | {v['nome']} | {desc_item_curta} ({v['severidade'].upper()})"
                    while texto_vuln and self.fonte_p.size(texto_vuln)[0] > r_item.width - 14:
                        texto_vuln = texto_vuln[:-1]
                    self.tela.blit(self.fonte_p.render(texto_vuln, True, cor_txt), (r_item.x + 10, r_item.y + 3))
                    self.rects_vulns.append((r_item, v))

            painel_desc_vuln = pygame.Rect(600, 405, 400, 163)
            desc_atual = self.vuln_desc.texto.strip()
            hover_desc_vuln = bool(desc_atual and painel_desc_vuln.collidepoint(pos_mouse) and not self.vuln_modelo.menu_aberto and not self.descricao_expandida)
            pygame.draw.rect(self.tela, (12, 20, 32) if hover_desc_vuln else (8, 12, 20), painel_desc_vuln)
            pygame.draw.rect(self.tela, COR_CIANO_NEON, painel_desc_vuln, 2 if hover_desc_vuln else 1)
            self.tela.set_clip(painel_desc_vuln.inflate(-6, -6))
            self.tela.blit(self.fonte_m.render("ENTENDA A FALHA E COMO CORRIGIR", True, COR_CIANO_NEON), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 8))

            if desc_atual:
                sev_atual = self.vuln_sev.texto.strip().lower()
                if sev_atual == 'baixa': cor_sev_desc = COR_AMBAR
                elif sev_atual == 'media': cor_sev_desc = COR_LARANJA
                elif sev_atual == 'alta': cor_sev_desc = COR_VERMELHO_CLARO
                else: cor_sev_desc = COR_VERMELHO_ESCURO

                titulo_curto_v = desc_atual if len(desc_atual) <= 18 else desc_atual[:16].rstrip() + "..."
                cabecalho_desc = f"Falha: {titulo_curto_v} | CVE: {self.vuln_cve.texto or 'N/A'} | {(sev_atual or 'N/A').upper()}"
                while cabecalho_desc and self.fonte_p.size(cabecalho_desc)[0] > painel_desc_vuln.width - 20:
                    cabecalho_desc = cabecalho_desc[:-1]
                self.tela.blit(self.fonte_p.render(cabecalho_desc, True, cor_sev_desc), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 30))

                texto_explicativo = DESCRICOES_DIDATICAS_VULN.get(desc_atual.casefold(), desc_atual)
                palavras_exp = texto_explicativo.split(' ')
                linhas_exp = []
                linha_atual_exp = ""
                for p in palavras_exp:
                    teste_exp = (linha_atual_exp + " " + p).strip()
                    if self.fonte_p.size(teste_exp)[0] <= painel_desc_vuln.width - 20:
                        linha_atual_exp = teste_exp
                    else:
                        if linha_atual_exp:
                            linhas_exp.append(linha_atual_exp)
                        linha_atual_exp = p
                if linha_atual_exp:
                    linhas_exp.append(linha_atual_exp)

                linhas_resumo_v = linhas_exp[:3]
                if len(linhas_exp) > 3 and len(linhas_resumo_v[-1]) > 3:
                    linhas_resumo_v[-1] = linhas_resumo_v[-1][:-3].rstrip() + "..."
                for idx_e, l_exp in enumerate(linhas_resumo_v):
                    self.tela.blit(self.fonte_p.render(l_exp, True, COR_TEXTO), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 52 + (idx_e * 19)))

                self.tela.blit(self.fonte_p.render("Clique abaixo para ler tudo e ver a correção:", True, COR_VERDE_MATRIX), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 112))
                rect_btn_ver_v = pygame.Rect(painel_desc_vuln.x + 10, painel_desc_vuln.bottom - 30, painel_desc_vuln.width - 20, 24)
                pygame.draw.rect(self.tela, (18, 42, 60) if hover_desc_vuln else (12, 26, 40), rect_btn_ver_v, border_radius=4)
                pygame.draw.rect(self.tela, COR_CIANO_NEON, rect_btn_ver_v, 1, border_radius=4)
                txt_btn_v = self.fonte_p.render("+ EXPANDIR EXPLICAÇÃO E CORREÇÃO", True, COR_CIANO_NEON)
                self.tela.blit(txt_btn_v, (rect_btn_ver_v.centerx - txt_btn_v.get_width() // 2, rect_btn_ver_v.y + 3))
            else:
                self.tela.blit(self.fonte_p.render("Escolha uma falha no menu à esquerda ou clique", True, COR_TEXTO_MUTED), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 42))
                self.tela.blit(self.fonte_p.render("em uma falha aberta acima para entender o que", True, COR_TEXTO_MUTED), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 62))
                self.tela.blit(self.fonte_p.render("ela significa e qual é a correção indicada.", True, COR_TEXTO_MUTED), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 82))
                self.tela.blit(self.fonte_p.render("-> Para corrigir falhas, acesse o SERVIDOR.", True, COR_AMBAR), (painel_desc_vuln.x + 10, painel_desc_vuln.y + 122))
            self.tela.set_clip(None)
            
            btn_patch = pygame.Rect(280, 520, 300, 48)
            pygame.draw.rect(self.tela, (60, 0, 0), btn_patch)
            pygame.draw.rect(self.tela, COR_VERMELHO_NEON, btn_patch, 2)
            self.tela.blit(self.fonte_m.render("CADASTRAR FALHA", True, COR_TEXTO), (btn_patch.x + 68, btn_patch.y + 14))

            if self.mensagem_status:
                msg_vuln = self.mensagem_status
                while msg_vuln and self.fonte_m.size(msg_vuln)[0] > rect_modal.width - 60:
                    msg_vuln = msg_vuln[:-1]
                self.tela.blit(self.fonte_m.render(msg_vuln, True, self.cor_status), (280, 582))

            self.vuln_modelo.desenhar_menu(self.tela)

        if self.descricao_expandida and self.modal_ativo in ["SERVIDOR_INFRA", "VULN_PATCH"]:
            if self.modal_ativo == "SERVIDOR_INFRA" and self.vuln_selecionada_servidor:
                nome_falha_exp = str(self.vuln_selecionada_servidor.get('descricao', '')).strip()
                cve_falha_exp = str(self.vuln_selecionada_servidor.get('cve', 'N/A')).strip()
                sev_falha_exp = str(self.vuln_selecionada_servidor.get('severidade', 'baixa')).strip()
                cat_falha_exp = str(self.vuln_selecionada_servidor.get('categoria', '')).strip()
            else:
                nome_falha_exp = self.vuln_desc.texto.strip()
                cve_falha_exp = self.vuln_cve.texto.strip() or "N/A"
                sev_falha_exp = self.vuln_sev.texto.strip() or "N/A"
                cat_falha_exp = self.vuln_cat.texto.strip()

            if nome_falha_exp:
                sombra_exp = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
                sombra_exp.fill((2, 5, 10, 185))
                self.tela.blit(sombra_exp, (0, 0))

                rect_exp = pygame.Rect(310, 130, 660, 440)
                pygame.draw.rect(self.tela, (10, 16, 26), rect_exp, border_radius=8)
                pygame.draw.rect(self.tela, COR_CIANO_NEON, rect_exp, 2, border_radius=8)

                sev_low = sev_falha_exp.lower()
                if sev_low == 'baixa': cor_sev_exp = COR_AMBAR
                elif sev_low == 'media': cor_sev_exp = COR_LARANJA
                elif sev_low == 'alta': cor_sev_exp = COR_VERMELHO_CLARO
                else: cor_sev_exp = COR_VERMELHO_ESCURO

                titulo_exp = f"FALHA: {nome_falha_exp.upper()}"
                titulo_exp_cortado = titulo_exp
                while titulo_exp_cortado and self.fonte_g.size(titulo_exp_cortado)[0] > rect_exp.width - 48:
                    titulo_exp_cortado = titulo_exp_cortado[:-1]
                if titulo_exp_cortado != titulo_exp and len(titulo_exp_cortado) > 3:
                    titulo_exp_cortado = titulo_exp_cortado[:-3].rstrip() + "..."
                self.tela.blit(self.fonte_g.render(titulo_exp_cortado, True, COR_CIANO_NEON), (rect_exp.x + 24, rect_exp.y + 20))
                self.tela.blit(self.fonte_m.render(f"Código: {cve_falha_exp}   |   Gravidade: {sev_falha_exp.upper()}", True, cor_sev_exp), (rect_exp.x + 24, rect_exp.y + 54))

                box_erro = pygame.Rect(rect_exp.x + 20, rect_exp.y + 86, rect_exp.width - 40, 145)
                pygame.draw.rect(self.tela, (14, 22, 34), box_erro, border_radius=6)
                pygame.draw.rect(self.tela, (40, 65, 95), box_erro, 1, border_radius=6)
                self.tela.blit(self.fonte_m.render("O QUE É ESTA FALHA:", True, COR_AMBAR), (box_erro.x + 14, box_erro.y + 10))

                texto_erro_completo = DESCRICOES_DIDATICAS_VULN.get(nome_falha_exp.casefold(), nome_falha_exp)
                palavras_ec = texto_erro_completo.split(' ')
                linhas_ec = []
                linha_at_ec = ""
                for p in palavras_ec:
                    teste_ec = (linha_at_ec + " " + p).strip()
                    if self.fonte_p.size(teste_ec)[0] <= box_erro.width - 28:
                        linha_at_ec = teste_ec
                    else:
                        if linha_at_ec:
                            linhas_ec.append(linha_at_ec)
                        linha_at_ec = p
                if linha_at_ec:
                    linhas_ec.append(linha_at_ec)

                for idx_ec, l_ec in enumerate(linhas_ec[:5]):
                    self.tela.blit(self.fonte_p.render(l_ec, True, COR_TEXTO), (box_erro.x + 14, box_erro.y + 38 + (idx_ec * 20)))

                box_fix = pygame.Rect(rect_exp.x + 20, rect_exp.y + 244, rect_exp.width - 40, 115)
                pygame.draw.rect(self.tela, (10, 26, 18), box_fix, border_radius=6)
                pygame.draw.rect(self.tela, COR_VERDE_MATRIX, box_fix, 1, border_radius=6)
                self.tela.blit(self.fonte_m.render("POSSÍVEL CORREÇÃO RECOMENDADA:", True, COR_VERDE_MATRIX), (box_fix.x + 14, box_fix.y + 10))

                texto_fix_completo = self.obter_sugestao_vuln(nome_falha_exp, cve_falha_exp, cat_falha_exp)
                palavras_fc = texto_fix_completo.split(' ')
                linhas_fc = []
                linha_at_fc = ""
                for p in palavras_fc:
                    teste_fc = (linha_at_fc + " " + p).strip()
                    if self.fonte_p.size(teste_fc)[0] <= box_fix.width - 28:
                        linha_at_fc = teste_fc
                    else:
                        if linha_at_fc:
                            linhas_fc.append(linha_at_fc)
                        linha_at_fc = p
                if linha_at_fc:
                    linhas_fc.append(linha_at_fc)

                for idx_fc, l_fc in enumerate(linhas_fc[:3]):
                    self.tela.blit(self.fonte_p.render(l_fc, True, COR_TEXTO), (box_fix.x + 14, box_fix.y + 38 + (idx_fc * 21)))

                if self.modal_ativo == "SERVIDOR_INFRA":
                    rect_btn_sugestao = pygame.Rect(340, 505, 310, 42)
                    pygame.draw.rect(self.tela, (12, 55, 25), rect_btn_sugestao, border_radius=5)
                    pygame.draw.rect(self.tela, COR_VERDE_MATRIX, rect_btn_sugestao, 2, border_radius=5)
                    txt_sug = self.fonte_p.render("USAR ESTA SUGESTÃO NA CORREÇÃO", True, COR_VERDE_MATRIX)
                    self.tela.blit(txt_sug, (rect_btn_sugestao.centerx - txt_sug.get_width() // 2, rect_btn_sugestao.y + 12))

                    rect_btn_fechar = pygame.Rect(670, 505, 270, 42)
                    pygame.draw.rect(self.tela, (20, 35, 52), rect_btn_fechar, border_radius=5)
                    pygame.draw.rect(self.tela, COR_CIANO_NEON, rect_btn_fechar, 1, border_radius=5)
                    txt_fch = self.fonte_p.render("FECHAR DETALHES", True, COR_CIANO_NEON)
                    self.tela.blit(txt_fch, (rect_btn_fechar.centerx - txt_fch.get_width() // 2, rect_btn_fechar.y + 12))
                else:
                    rect_btn_fechar = pygame.Rect(500, 505, 280, 42)
                    pygame.draw.rect(self.tela, (20, 35, 52), rect_btn_fechar, border_radius=5)
                    pygame.draw.rect(self.tela, COR_CIANO_NEON, rect_btn_fechar, 1, border_radius=5)
                    txt_fch = self.fonte_p.render("FECHAR DETALHES", True, COR_CIANO_NEON)
                    self.tela.blit(txt_fch, (rect_btn_fechar.centerx - txt_fch.get_width() // 2, rect_btn_fechar.y + 12))

    def desenhar_cursor(self):
        if not pygame.mouse.get_focused():
            return

        mx, my = pygame.mouse.get_pos()
        clicando = pygame.mouse.get_pressed()[0]

        if self.alerta_ativo and self.objeto_em_hover == "WORKSTATION":
            cor_borda = self.cor_alerta_atual
        elif self.objeto_em_hover == "SERVIDOR":
            cor_borda = COR_AMBAR
        else:
            cor_borda = COR_VERDE_MATRIX

        if clicando:
            pygame.draw.circle(self.tela, COR_AMBAR, (mx, my), 10, 1)
        elif self.objeto_em_hover and not self.modal_ativo:
            pygame.draw.circle(self.tela, cor_borda, (mx, my), 7, 1)

        pontos = [
            (mx, my),
            (mx, my + 18),
            (mx + 5, my + 14),
            (mx + 9, my + 22),
            (mx + 12, my + 20),
            (mx + 8, my + 12),
            (mx + 14, my + 12)
        ]
        pygame.draw.polygon(self.tela, COR_FUNDO, pontos)
        pygame.draw.polygon(self.tela, cor_borda, pontos, 2)

