# -*- coding: utf-8 -*-
"""
Tela de Logon do CyberPixel OS.
Projeto CyberPixel SOC - Bacharelado em Cibersegurança (UFU)
"""

import math
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
    SPRITE_BUG_TECLADO_MOUSE,
    PALETA_BUG_TECLADO_MOUSE,
    SPRITE_USER_CONVIDADO,
    PALETA_USER_CONVIDADO,
    SPRITE_POWER,
    PALETA_POWER
)
from interface.terminal_login import executar_terminal
from interface.tela_troca_senha import executar_tela_troca_senha
from sistema.usuarios import tentar_login, esta_bloqueado, tempo_restante_bloqueio


def executar_tela_login(tela, relogio):
    """
    Executa a interface de autenticação do CyberPixel OS.
    Retorna: (dados_usuario_autenticado, 'LOGIN') ou (None, 'DESLIGAR').
    """
    pygame.key.set_repeat(250, 40)

    fonte_titulo = pygame.font.SysFont("Trebuchet MS, Arial, sans-serif", 32, bold=True)
    fonte_subtitulo = pygame.font.SysFont("Trebuchet MS, Arial, sans-serif", 15)
    fonte_nome = pygame.font.SysFont("Tahoma, Arial, sans-serif", 18, bold=True)
    fonte_perfil = pygame.font.SysFont("Tahoma, Arial, sans-serif", 13)
    fonte_senha = pygame.font.SysFont("Consolas, Courier New", 18)
    fonte_msg = pygame.font.SysFont("Tahoma, Arial, sans-serif", 13, bold=True)

    usuario_selecionado = "convidado"
    senha_digitada = ""
    mensagem_erro = ""
    frames_tremor = 0

    rect_card_conv = pygame.Rect(640, 210, 520, 85)
    rect_area_senha = pygame.Rect(640, 315, 520, 110)
    rect_caixa_senha = pygame.Rect(640, 355, 410, 36)
    rect_btn_entrar = pygame.Rect(1060, 355, 100, 36)
    rect_btn_desligar = pygame.Rect(40, ALTURA_TELA - 65, 230, 40)

    try:
        while True:
            pos_mouse = pygame.mouse.get_pos()
            bloqueado = esta_bloqueado("login")
            segundos_bloqueio = tempo_restante_bloqueio("login")

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return None, "DESLIGAR"

                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if rect_btn_desligar.collidepoint(pos_mouse):
                        return None, "DESLIGAR"

                    if rect_btn_entrar.collidepoint(pos_mouse) and not bloqueado:
                        sucesso, resultado, restante = tentar_login(usuario_selecionado, senha_digitada)
                        if sucesso:
                            if resultado.get("senha_temporaria"):
                                usr_trocado, acao_troca = executar_tela_troca_senha(tela, relogio, resultado, senha_digitada)
                                if acao_troca == "LOGIN":
                                    return usr_trocado, "LOGIN"
                                elif acao_troca == "DESLIGAR":
                                    return None, "DESLIGAR"
                                else:
                                    senha_digitada = ""
                                    mensagem_erro = ""
                                    continue
                            return resultado, "LOGIN"
                        else:
                            mensagem_erro = resultado
                            frames_tremor = 20
                            senha_digitada = ""

                    elif rect_caixa_senha.collidepoint(pos_mouse):
                        pass

                elif evento.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()

                    # Atalho para o Terminal Administrativo
                    if evento.key == pygame.K_t and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_ALT):
                        dados_term, acao_term = executar_terminal(tela, relogio)
                        pygame.key.set_repeat(250, 40)
                        if acao_term == "LOGIN":
                            if dados_term.get("senha_temporaria"):
                                usr_trocado, acao_troca = executar_tela_troca_senha(
                                    tela, relogio, dados_term, dados_term.get("_senha_digitada", "")
                                )
                                if acao_troca == "LOGIN":
                                    return usr_trocado, "LOGIN"
                                elif acao_troca == "DESLIGAR":
                                    return None, "DESLIGAR"
                                else:
                                    senha_digitada = ""
                                    mensagem_erro = ""
                                    continue
                            return dados_term, "LOGIN"
                        elif acao_term == "DESLIGAR":
                            return None, "DESLIGAR"
                        senha_digitada = ""
                        mensagem_erro = ""

                    elif evento.key == pygame.K_ESCAPE:
                        return None, "DESLIGAR"

                    elif evento.key == pygame.K_RETURN:
                        if not bloqueado:
                            sucesso, resultado, restante = tentar_login(usuario_selecionado, senha_digitada)
                            if sucesso:
                                if resultado.get("senha_temporaria"):
                                    usr_trocado, acao_troca = executar_tela_troca_senha(tela, relogio, resultado, senha_digitada)
                                    if acao_troca == "LOGIN":
                                        return usr_trocado, "LOGIN"
                                    elif acao_troca == "DESLIGAR":
                                        return None, "DESLIGAR"
                                    else:
                                        senha_digitada = ""
                                        mensagem_erro = ""
                                        continue
                                return resultado, "LOGIN"
                            else:
                                mensagem_erro = resultado
                                frames_tremor = 20
                                senha_digitada = ""

                    elif evento.key == pygame.K_BACKSPACE:
                        senha_digitada = senha_digitada[:-1]

                    else:
                        char = evento.unicode
                        if char and char.isprintable() and len(senha_digitada) < 32:
                            senha_digitada += char
                            mensagem_erro = ""

            # Renderização da tela
            tela.fill(COR_OS_FUNDO)

            # Grid de fundo
            for x in range(0, LARGURA_TELA, 40):
                pygame.draw.line(tela, (5, 25, 12), (x, 75), (x, ALTURA_TELA - 80), 1)
            for y in range(75, ALTURA_TELA - 80, 40):
                pygame.draw.line(tela, (5, 25, 12), (0, y), (LARGURA_TELA, y), 1)

            # Barra superior
            pygame.draw.rect(tela, (6, 12, 8), (0, 0, LARGURA_TELA, 75))
            pygame.draw.line(tela, COR_OS_VERDE, (0, 75), (LARGURA_TELA, 75), 2)

            # Barra inferior
            pygame.draw.rect(tela, (6, 12, 8), (0, ALTURA_TELA - 80, LARGURA_TELA, 80))
            pygame.draw.line(tela, COR_OS_VERDE, (0, ALTURA_TELA - 80), (LARGURA_TELA, ALTURA_TELA - 80), 2)

            # Logotipo e título (sem sobreposição)
            desenhar_sprite(tela, SPRITE_BUG_TECLADO_MOUSE, PALETA_BUG_TECLADO_MOUSE, 90, 200, tam_px=7)
            tela.blit(fonte_titulo.render("CyberPixel OS", True, COR_OS_VERDE), (240, 210))
            tela.blit(fonte_subtitulo.render("Estação de Trabalho Didática - Laboratório Isolado", True, COR_OS_TEXTO_MUTED), (240, 250))

            # Linha divisória vertical
            pygame.draw.line(tela, COR_OS_VERDE_ESCURO, (600, 120), (600, ALTURA_TELA - 120), 2)

            # Cartão do usuário Convidado
            pygame.draw.rect(tela, COR_OS_PAINEL, rect_card_conv, border_radius=6)
            pygame.draw.rect(tela, COR_OS_VERDE, rect_card_conv, 2, border_radius=6)
            desenhar_sprite(tela, SPRITE_USER_CONVIDADO, PALETA_USER_CONVIDADO, rect_card_conv.x + 16, rect_card_conv.y + 16, tam_px=4)

            tela.blit(fonte_nome.render("Usuário Convidado", True, COR_OS_VERDE), (rect_card_conv.x + 90, rect_card_conv.y + 16))
            tela.blit(fonte_perfil.render("Ambiente do Aluno - Acesso a ferramentas locais", True, (160, 230, 180)), (rect_card_conv.x + 90, rect_card_conv.y + 44))

            # Área do campo de senha
            pygame.draw.rect(tela, (4, 14, 8), rect_area_senha, border_radius=6)
            pygame.draw.rect(tela, COR_OS_VERDE_ESCURO, rect_area_senha, 1, border_radius=6)
            tela.blit(fonte_perfil.render("SENHA DE ACESSO:", True, COR_OS_VERDE), (rect_area_senha.x + 16, rect_area_senha.y + 12))

            # Efeito de tremor em caso de erro
            offset_x = 0
            if frames_tremor > 0:
                offset_x = int(math.sin(frames_tremor * 1.5) * 6)
                frames_tremor -= 1

            caixa_animada = pygame.Rect(rect_caixa_senha.x + offset_x, rect_caixa_senha.y, rect_caixa_senha.width, rect_caixa_senha.height)
            btn_animado = pygame.Rect(rect_btn_entrar.x + offset_x, rect_btn_entrar.y, rect_btn_entrar.width, rect_btn_entrar.height)

            pygame.draw.rect(tela, (2, 8, 4), caixa_animada, border_radius=4)
            cor_borda_cx = (255, 60, 60) if frames_tremor > 0 else (COR_OS_VERDE if not bloqueado else (100, 100, 100))
            pygame.draw.rect(tela, cor_borda_cx, caixa_animada, 2, border_radius=4)

            # Senha mascarada
            txt_senha_masc = "*" * len(senha_digitada)
            img_senha = fonte_senha.render(txt_senha_masc + ("_" if pygame.time.get_ticks() % 800 < 400 and not bloqueado else ""), True, COR_OS_VERDE)
            tela.blit(img_senha, (caixa_animada.x + 12, caixa_animada.y + 8))

            # Botão [ > Entrar ]
            hover_entrar = btn_animado.collidepoint(pos_mouse) and not bloqueado
            cor_btn_e = (18, 115, 38) if hover_entrar else ((10, 60, 22) if not bloqueado else (40, 40, 40))
            pygame.draw.rect(tela, cor_btn_e, btn_animado, border_radius=4)
            pygame.draw.rect(tela, COR_OS_VERDE if not bloqueado else (70, 70, 70), btn_animado, 1, border_radius=4)
            txt_entrar = fonte_senha.render(">", True, (255, 255, 255) if not bloqueado else (120, 120, 120))
            tela.blit(txt_entrar, (btn_animado.centerx - txt_entrar.get_width() // 2, btn_animado.centery - txt_entrar.get_height() // 2 - 1))

            # Exibição de bloqueio ou erro
            if bloqueado:
                txt_bloq = fonte_msg.render(f"ACESSO BLOQUEADO: Aguarde {segundos_bloqueio} s", True, (255, 80, 80))
                tela.blit(txt_bloq, (rect_area_senha.x + 16, rect_area_senha.bottom - 22))
            elif mensagem_erro:
                txt_err = fonte_msg.render(mensagem_erro, True, (255, 90, 90))
                tela.blit(txt_err, (rect_area_senha.x + 16, rect_area_senha.bottom - 22))

            # Botão Desligar
            hover_desligar = rect_btn_desligar.collidepoint(pos_mouse)
            cor_desl = (140, 25, 25) if hover_desligar else (90, 15, 15)
            pygame.draw.rect(tela, cor_desl, rect_btn_desligar, border_radius=4)
            pygame.draw.rect(tela, (255, 70, 70), rect_btn_desligar, 1, border_radius=4)
            desenhar_sprite(tela, SPRITE_POWER, PALETA_POWER, rect_btn_desligar.x + 12, rect_btn_desligar.y + 10, tam_px=2)
            tela.blit(fonte_nome.render("Desligar", True, (255, 255, 255)), (rect_btn_desligar.x + 50, rect_btn_desligar.y + 8))

            pygame.display.flip()
            relogio.tick(FPS)

    finally:
        pygame.key.set_repeat(0)
