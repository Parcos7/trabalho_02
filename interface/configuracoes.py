# ==========================================
# SESSÃO: CONFIGURAÇÕES GERAIS E CONSTANTES
# ==========================================
LARGURA_TELA = 1280
ALTURA_TELA = 720
TITULO_JANELA = "CyberPixel - SOC Level 3 [Visual Interface]"
FPS = 50

# --- TEMA DARK ---
COR_FUNDO = (0, 0, 0)
COR_CHAO = (5, 5, 5)
COR_GRADE = (0, 40, 0)
COR_PAREDE = (6, 11, 20)
COR_TEXTO = (0, 255, 0)
COR_TEXTO_MUTED = (0, 150, 0)
COR_CIANO_NEON = (0, 255, 0)
COR_VERDE_MATRIX = (0, 255, 0)

# --- ESCALA CROMÁTICA DE ALERTAS E RISCO ---
COR_AMBAR = (200, 200, 0)              # Risco Baixo
COR_LARANJA = (255, 140, 0)            # Risco Médio
COR_VERMELHO_CLARO = (255, 80, 80)     # Risco Alto
COR_VERMELHO_ESCURO = (180, 0, 0)      # Risco Crítico
COR_VERMELHO_NEON = (255, 0, 0)        # Interface Padrão

COR_PAINEL = (0, 0, 0)
COR_PAINEL_BORDA = (0, 255, 0)

DESCRICOES_DIDATICAS_VULN = {
    "senha fraca": (
        "O aparelho usa uma senha muito simples ou fácil de adivinhar. "
        "Um invasor pode testar várias combinações automaticamente (ataque de força bruta) "
        "até descobrir a senha e entrar no sistema."
    ),
    "credenciais padrão": (
        "O equipamento ainda está com o usuário e a senha que vieram de fábrica (como admin/admin). "
        "Qualquer pessoa que conheça o modelo do aparelho pode consultar essa senha na internet "
        "e assumir o controle total."
    ),
    "vazamento de memória": (
        "Conhecida como Heartbleed: uma falha no sistema de criptografia (OpenSSL) permite que "
        "um invasor leia partes da memória RAM do servidor à distância, conseguindo roubar "
        "senhas e dados confidenciais sem deixar rastros."
    ),
    "rce via smbv1": (
        "Conhecida como EternalBlue: uma falha no compartilhamento de arquivos do Windows (SMBv1) "
        "permite que invasores enviem comandos remotamente para o computador e espalhem vírus "
        "(como ransomware) automaticamente pela rede da sala."
    ),
    "rce apache struts": (
        "Uma falha no sistema web Apache Struts permite que um atacante envie uma mensagem "
        "modificada pela rede e faça o servidor executar comandos perigosos por conta própria, "
        "comprometendo os dados armazenados."
    ),
    "rce via log4j": (
        "Conhecida como Log4Shell: quando o sistema registra um texto malicioso no histórico (log), "
        "a biblioteca Log4j interpreta esse texto como um comando e baixa arquivos invasores "
        "da internet automaticamente."
    ),
    "rce no spring": (
        "Conhecida como Spring4Shell: uma brecha no sistema Java Spring permite que um invasor "
        "envie requisições especiais para instalar um programa oculto dentro do servidor e "
        "controlar o equipamento à distância."
    )
}

CORRECOES_SUGERIDAS_VULN = {
    "senha fraca": "Troca da senha por uma senha forte com letras, números e símbolos e ativação de verificação em duas etapas.",
    "credenciais padrão": "Alteração imediata do usuário e senha de fábrica por credenciais exclusivas do administrador.",
    "vazamento de memória": "Atualização do pacote OpenSSL para versão corrigida e renovação dos certificados de segurança.",
    "rce via smbv1": "Instalação da atualização de segurança do sistema e desativação do protocolo antigo SMBv1.",
    "rce apache struts": "Atualização do Apache Struts para a versão segura e bloqueio de requisições suspeitas no firewall.",
    "rce via log4j": "Atualização da biblioteca Log4j para a versão 2.17 ou superior e bloqueio de conexões externas indevidas.",
    "rce no spring": "Atualização do pacote Spring Framework para a versão corrigida e revisão das permissões do servidor."
}
