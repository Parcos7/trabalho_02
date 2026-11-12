import os
import json
import hashlib
import secrets
import string
import time
from datetime import datetime

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_PROJETO = os.path.dirname(DIRETORIO_ATUAL)
CAMINHO_DADOS = os.path.join(DIRETORIO_PROJETO, "dados", "usuarios.json")
CAMINHO_SUDO = os.path.join(DIRETORIO_PROJETO, "dados", "sudo.json")
CAMINHO_BLOQUEIOS = os.path.join(DIRETORIO_PROJETO, "dados", "bloqueios.json")
CAMINHO_LOG_SEGURANCA = os.path.join(DIRETORIO_PROJETO, "logs", "seguranca.log")

ITERACOES_PBKDF2 = 100000
TEMPO_BLOQUEIO_SEGUNDOS = 30
MAX_TENTATIVAS_FALHAS = 3


def _garantir_diretorios():
    """Garante que as pastas dados e logs existam no projeto."""
    os.makedirs(os.path.dirname(CAMINHO_DADOS), exist_ok=True)
    os.makedirs(os.path.dirname(CAMINHO_LOG_SEGURANCA), exist_ok=True)


def _registrar_log_seguranca(evento, usuario_alvo, detalhe=""):
    """Registra eventos de auditoria sem jamais gravar senhas."""
    _garantir_diretorios()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensagem = f"[{data_hora}] [{evento}] Alvo: '{usuario_alvo}' | {detalhe}\n"
    try:
        with open(CAMINHO_LOG_SEGURANCA, "a", encoding="utf-8") as arq:
            arq.write(mensagem)
    except Exception:
        pass


def gerar_hash_senha(senha, salt_hex=None):
    """Gera hash PBKDF2-HMAC-SHA256 com 100.000 iterações e salt de 16 bytes."""
    if salt_hex is None:
        salt_bytes = secrets.token_bytes(16)
        salt_hex = salt_bytes.hex()
    else:
        salt_bytes = bytes.fromhex(salt_hex)

    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt_bytes,
        ITERACOES_PBKDF2
    )
    return salt_hex, hash_bytes.hex()


def verificar_senha(senha_digitada, salt_hex, hash_esperado_hex):
    """Compara senhas em tempo constante para evitar ataques de temporização."""
    if not salt_hex or not hash_esperado_hex:
        return False
    _, hash_gerado = gerar_hash_senha(senha_digitada, salt_hex)
    return secrets.compare_digest(hash_gerado, hash_esperado_hex)


# ==============================================================================
# PERSISTÊNCIA DE BLOQUEIOS E CONTADORES (LOGIN E SUDO)
# ==============================================================================

def carregar_bloqueios():
    _garantir_diretorios()
    padrao = {
        "login": {"falhas": 0, "bloqueado_ate": 0.0},
        "sudo": {"falhas": 0, "bloqueado_ate": 0.0}
    }
    if not os.path.exists(CAMINHO_BLOQUEIOS):
        return padrao
    try:
        with open(CAMINHO_BLOQUEIOS, "r", encoding="utf-8") as arq:
            dados = json.load(arq)
            for chave in padrao:
                if chave not in dados:
                    dados[chave] = padrao[chave]
            return dados
    except Exception:
        return padrao


def salvar_bloqueios(bloqueios):
    """Salva estado persistente de bloqueios em dados/bloqueios.json."""
    _garantir_diretorios()
    try:
        with open(CAMINHO_BLOQUEIOS, "w", encoding="utf-8") as arq:
            json.dump(bloqueios, arq, indent=4, ensure_ascii=False)
    except Exception:
        pass


def esta_bloqueado(tipo="login"):
    bloqueios = carregar_bloqueios()
    info = bloqueios.get(tipo, {})
    return time.time() < info.get("bloqueado_ate", 0.0)


def tempo_restante_bloqueio(tipo="login"):
    bloqueios = carregar_bloqueios()
    info = bloqueios.get(tipo, {})
    restante = int(info.get("bloqueado_ate", 0.0) - time.time())
    return max(0, restante)


def registrar_tentativa_falha(tipo="login", alvo=""):
    bloqueios = carregar_bloqueios()
    info = bloqueios.get(tipo, {"falhas": 0, "bloqueado_ate": 0.0})
    info["falhas"] = info.get("falhas", 0) + 1

    bloqueado = False
    segundos = 0

    if info["falhas"] >= MAX_TENTATIVAS_FALHAS:
        info["bloqueado_ate"] = time.time() + TEMPO_BLOQUEIO_SEGUNDOS
        info["falhas"] = 0
        bloqueado = True
        segundos = TEMPO_BLOQUEIO_SEGUNDOS
        _registrar_log_seguranca(
            "BLOQUEIO_ATIVADO",
            alvo or tipo,
            f"Bloqueio de {TEMPO_BLOQUEIO_SEGUNDOS}s aplicado em {tipo}."
        )
    else:
        _registrar_log_seguranca(
            "FALHA_AUTENTICACAO",
            alvo or tipo,
            f"Tentativa incorreta ({info['falhas']}/{MAX_TENTATIVAS_FALHAS}) em {tipo}."
        )

    bloqueios[tipo] = info
    salvar_bloqueios(bloqueios)
    return bloqueado, segundos


def limpar_falhas(tipo="login"):
    bloqueios = carregar_bloqueios()
    bloqueios[tipo] = {"falhas": 0, "bloqueado_ate": 0.0}
    salvar_bloqueios(bloqueios)


# ==============================================================================
# GERENCIAMENTO DE USUÁRIOS E SENHAS
# ==============================================================================

def carregar_usuarios():
    _garantir_diretorios()
    if not os.path.exists(CAMINHO_DADOS):
        return {}
    try:
        with open(CAMINHO_DADOS, "r", encoding="utf-8") as arq:
            return json.load(arq)
    except Exception:
        return {}


def salvar_usuarios(usuarios):
    _garantir_diretorios()
    with open(CAMINHO_DADOS, "w", encoding="utf-8") as arq:
        json.dump(usuarios, arq, indent=4, ensure_ascii=False)


def carregar_sudo():
    _garantir_diretorios()
    if not os.path.exists(CAMINHO_SUDO):
        return {}
    try:
        with open(CAMINHO_SUDO, "r", encoding="utf-8") as arq:
            return json.load(arq)
    except Exception:
        return {}


def definir_senha_sudo(nova_senha):
    _garantir_diretorios()
    salt_hex, hash_hex = gerar_hash_senha(nova_senha)
    dados = {
        "salt": salt_hex,
        "hash": hash_hex,
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(CAMINHO_SUDO, "w", encoding="utf-8") as arq:
        json.dump(dados, arq, indent=4, ensure_ascii=False)
    _registrar_log_seguranca("CONFIGURACAO_SUDO", "sistema", "Senha do sudo configurada.")
    return True


def verificar_senha_sudo(senha_digitada):
    if esta_bloqueado("sudo"):
        restante = tempo_restante_bloqueio("sudo")
        return False, f"sudo bloqueado. Aguarde {restante} s.", restante

    dados_sudo = carregar_sudo()
    if not dados_sudo:
        return False, "Senha do sudo não configurada.", 0

    salt = dados_sudo.get("salt", "")
    hash_esperado = dados_sudo.get("hash", "")

    if not verificar_senha(senha_digitada, salt, hash_esperado):
        bloqueado, segundos = registrar_tentativa_falha("sudo", "operador_terminal")
        if bloqueado:
            return False, f"3 erros consecutivos. sudo bloqueado por {segundos} s.", segundos
        return False, "Senha incorreta do sudo.", 0

    limpar_falhas("sudo")
    _registrar_log_seguranca("ACESSO_SUDO", "operador_terminal", "Comando administrativo autorizado.")
    return True, "Autorizado", 0


def tentar_login(usuario, senha_digitada):
    if esta_bloqueado("login"):
        restante = tempo_restante_bloqueio("login")
        return False, f"Acesso bloqueado. Aguarde {restante} s.", restante

    usuarios = carregar_usuarios()
    usuario_norm = str(usuario).strip().lower()

    if usuario_norm not in usuarios:
        bloqueado, segundos = registrar_tentativa_falha("login", usuario_norm)
        if bloqueado:
            return False, f"3 tentativas falhas. Bloqueado por {segundos} s.", segundos
        return False, "Credenciais incorretas.", 0

    dados_usuario = usuarios[usuario_norm]
    salt = dados_usuario.get("salt", "")
    hash_esperado = dados_usuario.get("hash", "")

    if not verificar_senha(senha_digitada, salt, hash_esperado):
        bloqueado, segundos = registrar_tentativa_falha("login", usuario_norm)
        if bloqueado:
            return False, f"3 tentativas falhas. Bloqueado por {segundos} s.", segundos
        return False, "Credenciais incorretas.", 0

    limpar_falhas("login")
    _registrar_log_seguranca("LOGIN_SUCESSO", usuario_norm, f"Perfil: {dados_usuario.get('perfil')}")
    return True, dados_usuario, 0


# ==============================================================================
# POLÍTICA DE SENHAS E CRIAÇÃO VIA SUDO
# ==============================================================================

def validar_politica_senha(senha, usuario="", senha_anterior=""):
    pendencias = []

    if len(senha) < 10:
        pendencias.append("Mínimo de 10 caracteres")
    if not any(c.isupper() for c in senha):
        pendencias.append("Pelo menos uma letra maiúscula")
    if not any(c.islower() for c in senha):
        pendencias.append("Pelo menos uma letra minúscula")
    if not any(c.isdigit() for c in senha):
        pendencias.append("Pelo menos um número")
    if not any(not c.isalnum() for c in senha):
        pendencias.append("Pelo menos um símbolo especial")

    if usuario and len(usuario) >= 3 and usuario.lower() in senha.lower():
        pendencias.append("Não deve conter o nome de usuário")

    if senha_anterior and senha == senha_anterior:
        pendencias.append("Deve ser diferente da senha temporária")

    return len(pendencias) == 0, pendencias


def gerar_senha_temporaria():
    maiusculas = string.ascii_uppercase
    minusculas = string.ascii_lowercase
    digitos = string.digits
    simbolos = "!@#$%^&*()-_=+"

    # Garante ao menos um caractere de cada categoria
    caracteres_iniciais = [
        secrets.choice(maiusculas),
        secrets.choice(minusculas),
        secrets.choice(digitos),
        secrets.choice(simbolos)
    ]
    todos = maiusculas + minusculas + digitos + simbolos
    restantes = [secrets.choice(todos) for _ in range(12)]

    lista_final = caracteres_iniciais + restantes
    secrets.SystemRandom().shuffle(lista_final)
    return "".join(lista_final)


def criar_usuario_sudo(nome_usuario):
    nome_norm = str(nome_usuario).strip().lower()

    if len(nome_norm) < 3 or len(nome_norm) > 16:
        return False, "", "O nome deve ter entre 3 e 16 caracteres."

    if not nome_norm.isalnum() or not nome_norm.islower():
        return False, "", "Use apenas letras minúsculas e números."

    if nome_norm in ["soc", "convidado"]:
        return False, "", "Nome de usuário reservado pelo sistema."

    usuarios = carregar_usuarios()
    if nome_norm in usuarios:
        return False, "", f"Usuário '{nome_norm}' já existe."

    senha_temp = gerar_senha_temporaria()
    salt_hex, hash_hex = gerar_hash_senha(senha_temp)

    usuarios[nome_norm] = {
        "usuario": nome_norm,
        "nome": nome_norm.capitalize(),
        "perfil": "comum",
        "salt": salt_hex,
        "hash": hash_hex,
        "senha_temporaria": True
    }
    salvar_usuarios(usuarios)

    # Registra no log de auditoria sem gravar a senha
    _registrar_log_seguranca("CADASTRO_USUARIO_SUDO", nome_norm, "Usuário criado com perfil comum e senha temporária.")
    return True, senha_temp, f"Usuário '{nome_norm}' criado com sucesso."


def atualizar_senha_usuario(usuario, nova_senha):
    """
    Atualiza a senha definitiva do usuário e desativa a flag de senha temporária.
    Retorna: (sucesso: bool, mensagem: str)
    """
    usuarios = carregar_usuarios()
    usuario_norm = str(usuario).strip().lower()

    if usuario_norm not in usuarios:
        return False, "Usuário não encontrado."

    valido, pendencias = validar_politica_senha(nova_senha, usuario=usuario_norm)
    if not valido:
        return False, "A nova senha não cumpre os requisitos: " + ", ".join(pendencias)

    salt_hex, hash_hex = gerar_hash_senha(nova_senha)
    usuarios[usuario_norm]["salt"] = salt_hex
    usuarios[usuario_norm]["hash"] = hash_hex
    usuarios[usuario_norm]["senha_temporaria"] = False

    salvar_usuarios(usuarios)
    _registrar_log_seguranca("TROCA_SENHA", usuario_norm, "Senha definitiva definida com sucesso.")
    return True, "Senha alterada com sucesso."


def cadastrar_usuario(solicitante, novo_usuario, nova_senha, nome, perfil):
    """Cadastro administrativo mantido para compatibilidade interna."""
    if not solicitante or solicitante.get("perfil") != "admin":
        _registrar_log_seguranca(
            "VIOLACAO_ACESSO",
            solicitante.get("usuario", "desconhecido") if solicitante else "anonimo",
            f"Tentativa não autorizada de cadastrar '{novo_usuario}'."
        )
        raise PermissionError("Apenas administradores podem cadastrar novos usuários.")

    usuario_norm = str(novo_usuario).strip().lower()
    if not usuario_norm or not nova_senha:
        raise ValueError("Usuário e senha são obrigatórios.")

    usuarios = carregar_usuarios()
    if usuario_norm in usuarios:
        raise ValueError("Usuário já existe.")

    salt_hex, hash_hex = gerar_hash_senha(nova_senha)
    usuarios[usuario_norm] = {
        "usuario": usuario_norm,
        "nome": str(nome).strip(),
        "perfil": str(perfil).strip().lower(),
        "salt": salt_hex,
        "hash": hash_hex,
        "senha_temporaria": False
    }
    salvar_usuarios(usuarios)
    _registrar_log_seguranca("CADASTRO_USUARIO", usuario_norm, f"Cadastrado por {solicitante.get('usuario')}")
    return True
