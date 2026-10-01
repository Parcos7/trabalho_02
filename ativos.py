class Ativo:
    def __init__(self, id_ativo: int, nome: str, responsavel: str, local: str):
        self.id = id_ativo
        self.nome = nome
        self.responsavel = responsavel
        self.local = local
        self.vulnerabilidades = []