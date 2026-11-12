import pygame
from interface.configuracoes import LARGURA_TELA, ALTURA_TELA, FPS, COR_OS_FUNDO, COR_OS_VERDE
from sistema.usuarios import (
    tentar_login,
    esta_bloqueado,
    tempo_restante_bloqueio,
    verificar_senha_sudo,
    criar_usuario_sudo
)


def executar_terminal(tela, relogio):
    pygame.key.set_repeat(250, 40)
    fonte_terminal = pygame.font.SysFont("Consolas, Courier New, monospace", 16)

    linhas = [
        "==================================================================",
        "  CyberPixel OS - Terminal Administrativo [Ambiente Seguro]",
        "  Digite 'help' para listar os comandos ou 'exit' para voltar.",
        "==================================================================",
        ""
    ]

    prompt_padrao = "lab@cyberpixel:~$ "
    comando_atual = ""
    
    # Modos de entrada: "COMANDO", "SENHA_LOGIN", "SENHA_SUDO"
    modo_entrada = "COMANDO"
    usuario_alvo = ""
    novo_usuario_alvo = ""
    senha_digitada = ""

    cursor_visivel = True
    ultimo_blink = pygame.time.get_ticks()

    try:
        while True:
            agora = pygame.time.get_ticks()
            if agora - ultimo_blink >= 500:
                cursor_visivel = not cursor_visivel
                ultimo_blink = agora

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return None, "DESLIGAR"

                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if modo_entrada != "COMANDO":
                            linhas.append("Operação cancelada pelo usuário.")
                            modo_entrada = "COMANDO"
                            senha_digitada = ""
                            comando_atual = ""
                        else:
                            return None, "FECHAR"

                    elif evento.key == pygame.K_BACKSPACE:
                        if modo_entrada != "COMANDO":
                            senha_digitada = senha_digitada[:-1]
                        else:
                            comando_atual = comando_atual[:-1]

                    elif evento.key == pygame.K_RETURN:
                        # 1. Processamento de senha de login de usuário
                        if modo_entrada == "SENHA_LOGIN":
                            linhas.append("Password: " + ("*" * len(senha_digitada)))
                            sucesso, resultado, restante = tentar_login(usuario_alvo, senha_digitada)
                            if sucesso:
                                resultado["_senha_digitada"] = senha_digitada
                                linhas.append(f"[SUCESSO] Sessão autorizada para '{usuario_alvo}'. Carregando...")
                                return resultado, "LOGIN"
                            else:
                                if esta_bloqueado("login"):
                                    linhas.append(f"[BLOQUEIO] Tentativas excedidas. Bloqueado por {restante} s.")
                                else:
                                    linhas.append(f"[ERRO] Falha de autenticação: {resultado}")
                            modo_entrada = "COMANDO"
                            usuario_alvo = ""
                            senha_digitada = ""
                            comando_atual = ""

                        # 2. Processamento de senha do comando sudo
                        elif modo_entrada == "SENHA_SUDO":
                            linhas.append("[sudo] senha: " + ("*" * len(senha_digitada)))
                            autenticado, msg_sudo, restante = verificar_senha_sudo(senha_digitada)
                            if not autenticado:
                                if esta_bloqueado("sudo"):
                                    linhas.append(f"[BLOQUEIO] Tentativas excedidas. sudo bloqueado por {restante} s.")
                                else:
                                    linhas.append(f"[ERRO] {msg_sudo}")
                            else:
                                sucesso_criacao, senha_temp, msg_criacao = criar_usuario_sudo(novo_usuario_alvo)
                                if sucesso_criacao:
                                    linhas.append(f"[SUCESSO] Usuário '{novo_usuario_alvo}' criado com sucesso!")
                                    linhas.append(f"Senha temporária: {senha_temp}")
                                    linhas.append("ATENÇÃO: Anote a senha. Ela não será exibida novamente.")
                                else:
                                    linhas.append(f"[ERRO] {msg_criacao}")

                            modo_entrada = "COMANDO"
                            novo_usuario_alvo = ""
                            senha_digitada = ""
                            comando_atual = ""

                        # 3. Processamento de comandos no prompt padrão
                        else:
                            cmd_limpo = comando_atual.strip()
                            linhas.append(prompt_padrao + comando_atual)
                            comando_atual = ""

                            if not cmd_limpo:
                                pass

                            elif cmd_limpo.lower() == "exit":
                                return None, "FECHAR"

                            elif cmd_limpo.lower() == "clear":
                                linhas.clear()

                            elif cmd_limpo.lower() == "help":
                                linhas.append("Comandos disponíveis:")
                                linhas.append("  help                      - Exibe esta lista de ajuda")
                                linhas.append("  login <usuario>           - Inicia sessão com a credencial informada")
                                linhas.append("  sudo criar_usuario <nome> - Cadastra um novo usuário no sistema")
                                linhas.append("  clear                     - Limpa o histórico da tela")
                                linhas.append("  exit                      - Encerra o terminal e retorna ao logon")

                            elif cmd_limpo.lower().startswith("login"):
                                partes = cmd_limpo.split()
                                if len(partes) < 2:
                                    linhas.append("Uso correto: login <usuario>")
                                else:
                                    alvo = partes[1].strip().lower()
                                    if esta_bloqueado("login"):
                                        linhas.append(f"[BLOQUEIO] Sistema temporariamente bloqueado ({tempo_restante_bloqueio('login')} s).")
                                    else:
                                        usuario_alvo = alvo
                                        modo_entrada = "SENHA_LOGIN"
                                        senha_digitada = ""

                            elif cmd_limpo.lower().startswith("sudo"):
                                partes = cmd_limpo.split()
                                if len(partes) == 3 and partes[1].lower() == "criar_usuario":
                                    nome_candidato = partes[2].strip().lower()
                                    if esta_bloqueado("sudo"):
                                        linhas.append(f"[BLOQUEIO] sudo bloqueado temporariamente ({tempo_restante_bloqueio('sudo')} s).")
                                    else:
                                        novo_usuario_alvo = nome_candidato
                                        modo_entrada = "SENHA_SUDO"
                                        senha_digitada = ""
                                else:
                                    linhas.append("Uso correto: sudo criar_usuario <nome>")

                            else:
                                linhas.append(f"comando não encontrado: '{cmd_limpo}'. Digite 'help' para ajuda.")

                    else:
                        char = evento.unicode
                        if char and char.isprintable():
                            if modo_entrada != "COMANDO":
                                if len(senha_digitada) < 32:
                                    senha_digitada += char
                            else:
                                if len(comando_atual) < 60:
                                    comando_atual += char

            # Renderização visual do terminal
            tela.fill(COR_OS_FUNDO)

            max_linhas_visiveis = (ALTURA_TELA - 45) // 22
            linhas_renderizadas = linhas[-max_linhas_visiveis:]

            y_pos = 15
            for linha in linhas_renderizadas:
                img_linha = fonte_terminal.render(linha, True, COR_OS_VERDE)
                tela.blit(img_linha, (20, y_pos))
                y_pos += 22

            # Renderização do prompt ou campo de senha ativa
            if modo_entrada == "SENHA_LOGIN":
                texto_prompt = "Password: " + ("*" * len(senha_digitada))
            elif modo_entrada == "SENHA_SUDO":
                texto_prompt = "[sudo] senha: " + ("*" * len(senha_digitada))
            else:
                texto_prompt = prompt_padrao + comando_atual

            cursor_str = "_" if cursor_visivel else " "
            img_prompt = fonte_terminal.render(texto_prompt + cursor_str, True, COR_OS_VERDE)
            tela.blit(img_prompt, (20, y_pos))

            pygame.display.flip()
            relogio.tick(FPS)

    finally:
        pygame.key.set_repeat(0)
