import getpass
from sistema.usuarios import (
    gerar_hash_senha,
    salvar_usuarios,
    carregar_usuarios,
    definir_senha_sudo,
    carregar_bloqueios,
    salvar_bloqueios
)


def configurar_usuarios_padrao():
    print("\n--- Configuração de Usuários do Sistema ---")
    
    # 1. Usuário SOC (Admin)
    senha_soc = ""
    while not senha_soc:
        senha_soc = getpass.getpass("Digite a senha para 'soc' (admin): ").strip()
        if not senha_soc:
            print("Erro: A senha não pode ser vazia.")
            continue
        confirma_soc = getpass.getpass("Confirme a senha para 'soc': ").strip()
        if senha_soc != confirma_soc:
            print("Erro: As senhas não conferem. Tente novamente.\n")
            senha_soc = ""

    # 2. Usuário Convidado (Comum)
    senha_conv = ""
    while not senha_conv:
        senha_conv = getpass.getpass("\nDigite a senha para 'convidado': ").strip()
        if not senha_conv:
            print("Erro: A senha não pode ser vazia.")
            continue
        confirma_conv = getpass.getpass("Confirme a senha para 'convidado': ").strip()
        if senha_conv != confirma_conv:
            print("Erro: As senhas não conferem. Tente novamente.\n")
            senha_conv = ""

    salt_soc, hash_soc = gerar_hash_senha(senha_soc)
    salt_conv, hash_conv = gerar_hash_senha(senha_conv)

    usuarios = carregar_usuarios()
    usuarios["soc"] = {
        "usuario": "soc",
        "nome": "Operador SOC",
        "perfil": "admin",
        "salt": salt_soc,
        "hash": hash_soc,
        "senha_temporaria": False
    }
    usuarios["convidado"] = {
        "usuario": "convidado",
        "nome": "Usuário Convidado",
        "perfil": "convidado",
        "salt": salt_conv,
        "hash": hash_conv,
        "senha_temporaria": False
    }

    salvar_usuarios(usuarios)
    print("\n[OK] Usuários 'soc' e 'convidado' configurados em dados/usuarios.json!")


def configurar_senha_sudo():
    print("\n--- Configuração da Senha do SUDO ---")
    senha_sudo = ""
    while not senha_sudo:
        senha_sudo = getpass.getpass("Digite a nova senha do [sudo]: ").strip()
        if not senha_sudo:
            print("Erro: A senha não pode ser vazia.")
            continue
        confirma = getpass.getpass("Confirme a senha do [sudo]: ").strip()
        if senha_sudo != confirma:
            print("Erro: As senhas não conferem. Tente novamente.\n")
            senha_sudo = ""

    definir_senha_sudo(senha_sudo)
    print("\n[OK] Senha do sudo salva com sucesso em dados/sudo.json!")


def main():
    print("=" * 60)
    print("   CyberPixel OS - Gerenciador de Credenciais Seguras")
    print("=" * 60)
    print("1 - Configurar usuários padrão (soc e convidado)")
    print("2 - Definir senha do sudo")
    print("3 - Configurar tudo (usuários padrão + sudo)")
    
    # Inicializa bloqueios se ainda não existirem
    salvar_bloqueios(carregar_bloqueios())

    opcao = input("\nEscolha uma opção (1, 2 ou 3): ").strip()
    if opcao == "1":
        configurar_usuarios_padrao()
    elif opcao == "2":
        configurar_senha_sudo()
    elif opcao == "3":
        configurar_usuarios_padrao()
        configurar_senha_sudo()
    else:
        print("Opção inválida. Executando configuração completa por padrão.")
        configurar_usuarios_padrao()
        configurar_senha_sudo()

    print("\n" + "=" * 60)
    print("Operação concluída. Nenhuma senha em texto puro foi gravada.")
    print("=" * 60)


if __name__ == "__main__":
    main()
