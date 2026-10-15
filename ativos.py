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
        self.dependencias = []

    def adicionar_vulnerabilidade(self, vulnerabilidade: dict):
        self.vulnerabilidades.append(vulnerabilidade)

    def exibir_informacoes(self):
        print(f"\n[ID: {self.id}] - {self.nome}\n"\
              f"Responsável: {self.responsavel} | Local: {self.local}\n" \
              f"Total de vulnerabilidades: {len(self.vulnerabilidades)}")

    @abstractmethod
    def fator_exposicao(self):
        return 0.8

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