from abc import ABC, abstractmethod

class Equipamento(ABC):
    PESOS_SEVERIDADE = {'baixa': 1.0, 'media': 2.5, 'alta': 5.0, 'critica': 10.0}
    STATUS_ABERTO = 'aberto'
    STATUS_FECHADO = 'fechado'
    STATUS_FECHADOS = frozenset({'fechado', 'fechada', 'corrigida', 'closed', 'resolved'})

    def __init__(self, id_ativo: int, nome: str, responsavel: str, local: str):
        self.id = id_ativo
        self.nome = nome
        self.responsavel = responsavel
        self.local = local
        self.vulnerabilidades = []
        self.dependencias = []

    def adicionar_vulnerabilidade(self, vulnerabilidade: dict):
        self.vulnerabilidades.append(vulnerabilidade)

    @classmethod
    def normalizar_status_vulnerabilidade(cls, status):
        status_normalizado = str(status).strip().lower()
        if status_normalizado in cls.STATUS_FECHADOS:
            return cls.STATUS_FECHADO
        return cls.STATUS_ABERTO

    @classmethod
    def vulnerabilidade_esta_aberta(cls, vulnerabilidade):
        return cls.normalizar_status_vulnerabilidade(vulnerabilidade.get('status', '')) == cls.STATUS_ABERTO

    @abstractmethod
    def fator_exposicao(self):
        return 0.8

    def calcular_risco(self, risco_base=None):
        if risco_base is None:
            risco_base = sum(
                self.PESOS_SEVERIDADE.get(
                    str(vulnerabilidade.get('severidade', 'baixa')).strip().lower(),
                    1.0
                )
                for vulnerabilidade in self.vulnerabilidades
                if self.vulnerabilidade_esta_aberta(vulnerabilidade)
            )

        return risco_base * self.fator_exposicao()

    @staticmethod
    def fabricar_ativo(tipo_ativo, dados_ativos):
        match tipo_ativo:
            case "NOTEBOOK":
                return Notebook(dados_ativos['id'], dados_ativos['nome'], dados_ativos['responsavel'], dados_ativos['local'], dados_ativos.get('qnt_ram', 0))
            case "SERVIDOR":
                return Servidor(dados_ativos['id'], dados_ativos['nome'], dados_ativos['responsavel'], dados_ativos['local'], dados_ativos.get('sistema_operacional', 'N/A'))
            case "ROTEADOR":
                return Roteador(dados_ativos['id'], dados_ativos['nome'], dados_ativos['responsavel'], dados_ativos['local'], dados_ativos.get('firmware_atualizado', False))
            case "DESKTOP": 
                return Desktop(dados_ativos['id'], dados_ativos['nome'], dados_ativos['responsavel'], dados_ativos['local'], dados_ativos.get('qnt_ram', 0))

class Servidor(Equipamento):
    def __init__(self, id_ativo: int, nome: str, responsavel: str, local: str, sistema_operacional: str):
        super().__init__(id_ativo, nome, responsavel, local)
        self.sistema_operacional = sistema_operacional
        self.tipo = "SERVIDOR"
    
    def fator_exposicao(self):
        return 1.5

class Roteador(Equipamento):
    def __init__(self, id_ativo: int, nome: str, responsavel: str, local: str, firmware_atualizado: bool):
        super().__init__(id_ativo, nome, responsavel, local)
        self.firmware_atualizado = firmware_atualizado
        self.tipo = "ROTEADOR"
        
    def fator_exposicao(self):
        return 0.8

class Notebook(Equipamento):
    def __init__(self, id_ativo: int, nome:str, responsavel:str, local:str, qnt_ram: int):
        super().__init__(id_ativo, nome, responsavel, local)
        self.qnt_ram = qnt_ram
        self.tipo = "NOTEBOOK"
    
    def fator_exposicao(self):
        return 0.8
    
class Desktop(Equipamento):
    def __init__(self, id_ativo: int, nome:str, responsavel:str, local:str, qnt_ram: int):
        super().__init__(id_ativo, nome, responsavel, local)
        self.qnt_ram = qnt_ram
        self.tipo = "DESKTOP"
    
    def fator_exposicao(self):
        return 0.8