import os

class DeckLoader:
    @staticmethod
    def load_from_txt(file_path):
        """
        Lê um arquivo .txt e retorna uma lista simples de nomes de cartas.
        Exemplo do TXT:
        4 Lightning Bolt
        20 Mountain
        """
        deck_list = []
        
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): # Pula linhas vazias ou comentários
                    continue
                
                try:
                    # Tenta separar a quantidade do nome (ex: "4 Black Lotus")
                    parts = line.split(' ', 1)
                    if len(parts) > 1 and parts[0].isdigit():
                        quantity = int(parts[0])
                        card_name = parts[1]
                        for _ in range(quantity):
                            deck_list.append(card_name)
                    else:
                        deck_list.append(line)
                except:
                    continue
        
        return deck_list
