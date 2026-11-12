# -*- coding: utf-8 -*-
"""
Tela de Troca Obrigatória de Senha no Primeiro Login.
Projeto CyberPixel SOC - Bacharelado em Cibersegurança (UFU)
"""

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
from sistema.usuarios import validar_politica_senha, atualizar_senha_usuario, carregar_usuarios


def executar_tela_troca_senha(tela, relogio, dados_usuario, senha_temporaria=""):
    """
    Exibe a interface gráfica para definição de senha definitiva.
    Retorna: (dados_usuario_atualizados, 'LOGIN') ou (None, 'CANCELAR').
    """
    pygame.key.set_repeat(250, 40)

    fonte_titulo = pygame.font.SysFont("Trebuchet MS, Arial", 22, bold=True)
    fonte_rotulo = pygame.font.SysFont("Tahoma, Arial", 13, bold=True)
    fonte_campo = pygame.font.SysFont("Consolas, Courier New", 18)
    fonte_requisito = pygame.font.SysFont("Consolas, Courier New", 12)
    fonte_btn = pygame.font.SysFont("Tahoma, Arial", 13, bold=True)
    fonte_msg = pygame.font.SysFont("Tahoma, Arial", 12, bold=True)

    nome_usuario = dados_usuario.get("usuario", "usuario")
    nova_senha = ""
    confirma_senha = ""
    campo_foco = 1  # 1: nova_senha, 2: confirma_senha
    mensagem_erro = ""

    # Geometria do painel central
    largura_painel = 620
    altura_painel = 460
    rect_painel = pygame.Rect(
        (LARGURA_TELA - largura_painel) // 2,
        (ALTURA_TELA - altura_painel) // 2,
        largura_painel,
        altura_painel
    )

    rect_campo1 = pygame.Rect(rect_painel.x + 30, rect_painel.y + 100, 560, 34)
    rect_campo2 = pygame.Rect(rect_painel.x + 30, rect_painel.y + 165, 560, 34)
    rect_btn_confirmar = pygame.Rect(rect_painel.x + 30, rect_painel.bottom - 55, 260, 38)
    rect_btn_cancelar = pygame.Rect(rect_painel.right - 290, rect_painel.bottom - 55, 260, 38)

    try:
        while True:
            pos_mouse = pygame.mouse.get_pos()

            # Avaliação dos requisitos em tempo real
            req_tamanho = len(nova_senha) >= 10
            req_maiuscula = any(c.isupper() for c in nova_senha)
            req_minuscula = any(c.islower() for c in nova_senha)
            req_numero = any(c.isdigit() for c in nova_senha)
            req_simbolo = any(not c.isalnum() for c in nova_senha)
            req_usuario = len(nome_usuario) >= 3 and (nome_usuario.lower() not in nova_senha.lower())
            req_diferente = bool(nova_senha and nova_senha != senha_temporaria)
            req_conferem = bool(nova_senha and nova_senha == confirma_senha)

            politica_atendida = (
                req_tamanho and req_maiuscula and req_minuscula and
                req_numero and req_simbolo and req_usuario and req_diferente
            )

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return None, "DESLIGAR"

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if rect_campo1.collidepoint(pos_mouse):
                        campo_foco = 1
                    elif rect_campo2.collidepoint(pos_mouse):
                        campo_foco = 2

                    elif rect_btn_cancelar.collidepoint(pos_mouse):
                        return None, "CANCELAR"

                    elif rect_btn_confirmar.collidepoint(pos_mouse):
                        if not politica_atendida:
                            mensagem_erro = "A nova senha não atende a todos os requisitos abaixo."
                        elif not req_conferem:
                            mensagem_erro = "A confirmação de senha não confere."
                        else:
                            sucesso, msg = atualizar_senha_usuario(nome_usuario, nova_senha)
                            if sucesso:
                                usuarios = carregar_usuarios()
                                return usuarios.get(nome_usuario, dados_usuario), "LOGIN"
                            else:
                                mensagem_erro = msg

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return None, "CANCELAR"

                    elif evento.key == pygame.K_TAB:
                        campo_foco = 2 if campo_foco == 1 else 1

                    elif evento.key == pygame.K_BACKSPACE:
                        if campo_foco == 1:
                            nova_senha = nova_senha[:-1]
                        else:
                            confirma_senha = confirma_senha[:-1]

                    elif evento.key == pygame.K_RETURN:
                        if campo_foco == 1:
                            campo_foco = 2
                        else:
                            if not politica_atendida:
                                mensagem_erro = "A nova senha não atende a todos os requisitos abaixo."
                            elif not req_conferem:
                                mensagem_erro = "A confirmação de senha não confere."
                            else:
                                sucesso, msg = atualizar_senha_usuario(nome_usuario, nova_senha)
                                if sucesso:
                                    usuarios = carregar_usuarios()
                                    return usuarios.get(nome_usuario, dados_usuario), "LOGIN"
                                else:
                                    mensagem_erro = msg

                    else:
                        char = evento.unicode
                        if char and char.isprintable():
                            if campo_foco == 1 and len(nova_senha) < 32:
                                nova_senha += char
                                mensagem_erro = ""
                            elif campo_foco == 2 and len(confirma_senha) < 32:
                                confirma_senha += char
                                mensagem_erro = ""

            # Renderização gráfica
            tela.fill(COR_OS_FUNDO)

            # Painel central
            pygame.draw.rect(tela, COR_OS_PAINEL, rect_painel, border_radius=8)
            pygame.draw.rect(tela, COR_OS_VERDE, rect_painel, 2, border_radius=8)

            # Cabeçalho
            rect_topo = pygame.Rect(rect_painel.x, rect_painel.y, rect_painel.width, 48)
            pygame.draw.rect(tela, COR_OS_VERDE_ESCURO, rect_topo, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.line(tela, COR_OS_VERDE, (rect_painel.x, rect_topo.bottom), (rect_painel.right, rect_topo.bottom), 1)
            txt_tit = fonte_titulo.render("Troca Obrigatória de Senha (Primeiro Acesso)", True, (255, 255, 255))
            tela.blit(txt_tit, (rect_painel.x + 20, rect_painel.y + 12))

            # Identificação do usuário
            tela.blit(
                fonte_rotulo.render(f"Usuário: {nome_usuario}  (Defina sua senha definitiva pessoal)", True, COR_OS_VERDE),
                (rect_painel.x + 30, rect_painel.y + 58)
            )

            # Campo 1: Nova Senha
            tela.blit(fonte_rotulo.render("NOVA SENHA:", True, (220, 240, 220)), (rect_campo1.x, rect_campo1.y - 20))
            cor_borda1 = COR_OS_VERDE if campo_foco == 1 else COR_OS_VERDE_ESCURO
            pygame.draw.rect(tela, (3, 12, 6), rect_campo1, border_radius=4)
            pygame.draw.rect(tela, cor_borda1, rect_campo1, 1, border_radius=4)
            tela.blit(fonte_campo.render("*" * len(nova_senha), True, COR_OS_VERDE), (rect_campo1.x + 10, rect_campo1.y + 7))

            # Campo 2: Confirmar Senha
            tela.blit(fonte_rotulo.render("CONFIRMAR NOVA SENHA:", True, (220, 240, 220)), (rect_campo2.x, rect_campo2.y - 20))
            cor_borda2 = COR_OS_VERDE if campo_foco == 2 else COR_OS_VERDE_ESCURO
            pygame.draw.rect(tela, (3, 12, 6), rect_campo2, border_radius=4)
            pygame.draw.rect(tela, cor_borda2, rect_campo2, 1, border_radius=4)
            tela.blit(fonte_campo.render("*" * len(confirma_senha), True, COR_OS_VERDE), (rect_campo2.x + 10, rect_campo2.y + 7))

            # Área de Política de Senhas com indicadores em tempo real
            rect_reqs = pygame.Rect(rect_painel.x + 30, rect_painel.y + 215, 560, 140)
            pygame.draw.rect(tela, (4, 16, 8), rect_reqs, border_radius=4)
            pygame.draw.rect(tela, (12, 50, 25), rect_reqs, 1, border_radius=4)

            tela.blit(fonte_rotulo.render("Política de Segurança da Senha:", True, COR_OS_VERDE), (rect_reqs.x + 10, rect_reqs.y + 8))

            itens_check = [
                ("Mínimo de 10 caracteres", req_tamanho),
                ("Letra maiúscula (A-Z)", req_maiuscula),
                ("Letra minúscula (a-z)", req_minuscula),
                ("Número (0-9)", req_numero),
                ("Símbolo especial (!@#$...)", req_simbolo),
                ("Não conter o nome de usuário", req_usuario),
                ("Diferente da temporária", req_diferente),
                ("Senhas conferem", req_conferem)
            ]

            # Renderiza em duas colunas de 4 itens
            for i, (rotulo, cumprido) in enumerate(itens_check):
                col = i // 4
                lin = i % 4
                x_pos = rect_reqs.x + 15 + (col * 270)
                y_pos = rect_reqs.y + 32 + (lin * 24)

                cor_status = COR_OS_VERDE if cumprido else (150, 70, 70)
                simbolo_txt = "[OK]" if cumprido else "[ X]"
                tela.blit(fonte_requisito.render(f"{simbolo_txt} {rotulo}", True, cor_status), (x_pos, y_pos))

            # Mensagem de erro (se houver)
            if mensagem_erro:
                txt_err = fonte_msg.render(mensagem_erro, True, (255, 90, 90))
                tela.blit(txt_err, (rect_painel.centerx - txt_err.get_width() // 2, rect_painel.bottom - 80))

            # Botão Confirmar
            hover_conf = rect_btn_confirmar.collidepoint(pos_mouse)
            cor_conf = (20, 130, 50) if hover_conf else COR_OS_VERDE_ESCURO
            pygame.draw.rect(tela, cor_conf, rect_btn_confirmar, border_radius=4)
            pygame.draw.rect(tela, COR_OS_VERDE, rect_btn_confirmar, 1, border_radius=4)
            txt_btn_c = fonte_btn.render("Confirmar e Entrar", True, (255, 255, 255))
            tela.blit(txt_btn_c, (rect_btn_confirmar.centerx - txt_btn_c.get_width() // 2, rect_btn_confirmar.y + 10))

            # Botão Cancelar
            hover_canc = rect_btn_cancelar.collidepoint(pos_mouse)
            cor_canc = (120, 30, 30) if hover_canc else (80, 20, 20)
            pygame.draw.rect(tela, cor_canc, rect_btn_cancelar, border_radius=4)
            pygame.draw.rect(tela, (255, 80, 80), rect_btn_cancelar, 1, border_radius=4)
            txt_btn_x = fonte_btn.render("Cancelar e Sair", True, (255, 255, 255))
            tela.blit(txt_btn_x, (rect_btn_cancelar.centerx - txt_btn_c.get_width() // 2, rect_btn_cancelar.y + 10))

            pygame.display.flip()
            relogio.tick(FPS)

    finally:
        pygame.key.set_repeat(0)
