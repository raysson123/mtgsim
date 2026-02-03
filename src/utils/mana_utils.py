import re

class ManaUtils:
    @staticmethod
    def parse_mana_cost(cost_string):
        """
        Converte string do Scryfall '{2}{U}{G}' em dicionário:
        {'generic': 2, 'blue': 1, 'green': 1}
        """
        pool = {
            "white": 0, "blue": 0, "black": 0, 
            "red": 0, "green": 0, "colorless": 0, 
            "generic": 0
        }
        
        if not cost_string or not isinstance(cost_string, str):
            return pool

        # Regex para capturar tudo entre chaves { }
        simbolos = re.findall(r'\{([0-9A-Z/]+)\}', cost_string)

        mapa_cores = {
            "W": "white", "U": "blue", "B": "black",
            "R": "red", "G": "green", "C": "colorless"
        }

        for simb in simbolos:
            # Limpa o símbolo (caso venha com espaços ou minúsculas)
            simb = simb.strip().upper()

            # 1. Custo Genérico (Números)
            if simb.isdigit():
                pool["generic"] += int(simb)
            
            # 2. Símbolo Simples de Cor (W, U, B, R, G, C)
            elif simb in mapa_cores:
                pool[mapa_cores[simb]] += 1
            
            # 3. Custo Híbrido (Ex: {U/R})
            elif "/" in simb:
                partes = simb.split("/")
                # Consideramos a primeira parte para validação de custo simples
                cor_escolhida = partes[0]
                if cor_escolhida in mapa_cores:
                    pool[mapa_cores[cor_escolhida]] += 1
                elif cor_escolhida.isdigit():
                    pool["generic"] += int(cor_escolhida)

        return pool
