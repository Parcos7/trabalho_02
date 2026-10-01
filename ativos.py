# =====================================================================
# NOTA DE NOMENCLATURA PESSOAL:
# 'db'  -> Simplificação de "base de dados"
# 'arq' -> Simplificação de "ficheiros" ou "ficheiro"
# 'res' -> Simplificação de "Responsavel"
# 'loc' -> Simplificação de "Localidade"
# 'fw' -> Simplificação de "firmware"
# 'so' -> Simplificação de "Sistema Operacional"
# =====================================================================

from abc import ABC, abstractmethod

class Equipamento(ABC):
    def __init__(self, id_ativo: int, nome: str, responsavel: str, local: str):
        self.id = id_ativo
        self.nome = nome
        self.responsavel = responsavel
        self.local = local
        self.vulnerabilidades = []

    def adicionar_vulnerabilidade(self, vulnerabilidade: dict):
        self.vulnerabilidades.append(vulnerabilidade)

    def exibir_informacoes(self):
        print(f"\n[ID: {self.id}] - {self.nome}\n"\
              f"Responsável: {self.responsavel} | Local: {self.local}\n" \
              f"Total de vulnerabilidades: {len(self.vulnerabilidades)}")

    @abstractmethod
    def calcular_risco(self):
        pass

class Servidor(Equipamento):
    def __init__(self, id_ativo: int, nome: str, responsavel: str, local: str, sistema_operacional: str):
        super().__init__(id_ativo, nome, responsavel, local)
        self.sistema_operacional = sistema_operacional
        self.tipo = "SERVIDOR"

    def calcular_risco(self):
        return "Cálculo de Risco de Servidor "

class Roteador(Equipamento):
    def __init__(self, id_ativo: int, nome: str, responsavel: str, local: str, firmware_atualizado: bool):
        super().__init__(id_ativo, nome, responsavel, local)
        self.firmware_atualizado = firmware_atualizado
        self.tipo = "ROTEADOR"
    
    def calcular_risco(self):
        return "Cálculo de Risco de Roteador "

class Notebook(Equipamento):
    def __init__(self, id_ativo: int, nome:str, responsavel:str, local:str, qnt_ram: int):
        super().__init__(id_ativo, nome, responsavel, local)
        self.qnt_ram = qnt_ram
        self.tipo = "NOTEBOOK"

    def calcular_risco(self):
        return "Cálculo de risco de Notebook "

class Desktop(Equipamento):
    def __init__(self, id_ativo: int, nome:str, responsavel:str, local:str, qnt_ram: int):
        super().__init__(id_ativo, nome, responsavel, local)
        self.qnt_ram = qnt_ram
        self.tipo = "DESKTOP"

    def calcular_risco(self):
        return "Calculo de risco de Desktop "