ESTADO_PADRAO = [
    {
        "nome": "Pastas de Auditoria",
        "tipo": "Pasta de arquivos",
        "tamanho": "--",
        "eh_pasta": True,
        "conteudo": ""
    },
    {
        "nome": "Documentos de Rede",
        "tipo": "Pasta de arquivos",
        "tamanho": "--",
        "eh_pasta": True,
        "conteudo": ""
    },
    {
        "nome": "Manual_Seguranca_UFU.txt",
        "tipo": "Documento de Texto",
        "tamanho": "14 KB",
        "eh_pasta": False,
        "conteudo": (
            "====================================================\n"
            "   MANUAL DE SEGURANÇA DA INFORMAÇÃO - UFU\n"
            "====================================================\n\n"
            "1. POLÍTICA DE ISOLAMENTO:\n"
            "   Esta estação de trabalho pertence a um laboratório\n"
            "   didático isolado (air-gapped network). Não há rota\n"
            "   direta de saída para a internet externa.\n\n"
            "2. CONTROLE DE ACESSO (RBAC):\n"
            "   - Usuários 'convidado' têm acesso restrito aos utilitários\n"
            "     locais e não possuem privilégios de administração.\n"
            "   - O acesso ao Centro de Operações de Segurança (SOC)\n"
            "     é estritamente restrito aos operadores 'soc'.\n\n"
            "3. REGRA DE AUDITORIA:\n"
            "   Tentativas de força bruta ou comandos não autorizados\n"
            "   são registrados no arquivo de auditoria seguranca.log."
        )
    },
    {
        "nome": "politica_senhas.txt",
        "tipo": "Documento de Texto",
        "tamanho": "4 KB",
        "eh_pasta": False,
        "conteudo": (
            "====================================================\n"
            "   POLÍTICA DE SENHAS E CREDENCIAIS\n"
            "====================================================\n\n"
            "- Criptografia: PBKDF2-HMAC-SHA256 com 100.000 iterações.\n"
            "- Salteamento: 16 bytes criptograficamente seguros por usuário.\n"
            "- Tolerância a Falhas: Bloqueio temporário de 30 segundos\n"
            "  após 3 tentativas consecutivas incorretas."
        )
    },
    {
        "nome": "inventario_backup.bak",
        "tipo": "Arquivo de Backup",
        "tamanho": "48 KB",
        "eh_pasta": False,
        "conteudo": "[ARQUIVO BINÁRIO DE BACKUP DO INVENTÁRIO]"
    }
]


_arquivos_em_memoria = []


def reiniciar_sistema_arquivos():
    global _arquivos_em_memoria
    _arquivos_em_memoria = [dict(item) for item in ESTADO_PADRAO]


def listar_arquivos():
    global _arquivos_em_memoria
    if not _arquivos_em_memoria:
        reiniciar_sistema_arquivos()
    return _arquivos_em_memoria


def criar_nova_pasta():
    itens = listar_arquivos()
    nomes_existentes = {item["nome"] for item in itens if item["eh_pasta"]}

    if "Nova pasta" not in nomes_existentes:
        nome_pasta = "Nova pasta"
    else:
        contador = 2
        while f"Nova pasta ({contador})" in nomes_existentes:
            contador += 1
        nome_pasta = f"Nova pasta ({contador})"

    nova_pasta = {
        "nome": nome_pasta,
        "tipo": "Pasta de arquivos",
        "tamanho": "--",
        "eh_pasta": True,
        "conteudo": ""
    }
    itens.insert(0, nova_pasta)
    return nome_pasta


def obter_conteudo(nome_arquivo):
    for item in listar_arquivos():
        if item["nome"] == nome_arquivo:
            return item.get("conteudo", "")
    return ""


reiniciar_sistema_arquivos()
