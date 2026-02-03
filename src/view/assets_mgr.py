import pygame
import os
import requests
import json
import re # Importante para lidar com caracteres especiais

class AssetsManager:
    def __init__(self):
        # Define o caminho base como a pasta 'assets' na raiz do projeto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(base_dir, "..", "..", "assets")
        self.decks_dir = os.path.join(self.assets_dir, "decks")
        
        # Cria as pastas se não existirem
        os.makedirs(self.decks_dir, exist_ok=True)
        
        # Cache de imagens para não carregar do disco toda hora
        self.image_cache = {}
        
        # Imagem padrão (verso da carta)
        self.card_back = pygame.Surface((223, 310))
        self.card_back.fill((20, 20, 20)) # Fundo escuro
        pygame.draw.rect(self.card_back, (100, 100, 100), (10, 10, 203, 290), 2)
        # Um X no meio para indicar erro de carregamento visualmente
        pygame.draw.line(self.card_back, (100,50,50), (0,0), (223,310), 3)
        pygame.draw.line(self.card_back, (100,50,50), (223,0), (0,310), 3)

    def _sanitize_filename(self, name):
        """Remove caracteres proibidos no Windows e comuns em cartas (ex: //, :)"""
        # Substitui : e / por nada ou sublinhado para tentar achar o arquivo
        name = name.replace(" // ", "_") # Cartas duplas
        name = name.replace(":", "")     # Ex: Circle of Protection: Red
        name = name.replace("'", "")     # Ex: Bolas's Citadel -> Bolass Citadel
        name = name.replace("?", "")
        name = name.replace('"', "")
        return name

    def get_card_image(self, deck_name, card_name):
        """Retorna a Surface da imagem. Tenta variações de nome se não achar de primeira."""
        key = f"{deck_name}/{card_name}"
        if key in self.image_cache:
            return self.image_cache[key]
        
        folder = os.path.join(self.decks_dir, deck_name)
        
        # TENTATIVA 1: Nome Exato
        candidates = [
            f"{card_name}.jpg",
            f"{card_name}.png",
            f"{card_name}.jpeg"
        ]
        
        # TENTATIVA 2: Nome Sanitizado (Sem ' : ou //)
        clean_name = self._sanitize_filename(card_name)
        candidates.append(f"{clean_name}.jpg")
        
        # TENTATIVA 3: Nome Sanitizado mantendo espaços simples
        # Às vezes 'Bolas's' vira 'Bolass', às vezes 'Bolas'
        candidates.append(f"{card_name.replace("'", "")}.jpg")

        image_path = None
        for filename in candidates:
            path_temp = os.path.join(folder, filename)
            if os.path.exists(path_temp):
                image_path = path_temp
                break
        
        if image_path:
            try:
                img = pygame.image.load(image_path).convert()
                img = pygame.transform.scale(img, (223, 310))
                self.image_cache[key] = img
                return img
            except Exception as e:
                print(f"Erro ao carregar imagem {card_name} (Path: {image_path}): {e}")
        else:
            print(f"IMAGEM NÃO ENCONTRADA: {card_name} (Tentado: {candidates})")
        
        return self.card_back

    def get_card_data(self, deck_name, card_name):
        """Lê o JSON do deck e retorna os dados da carta."""
        json_path = os.path.join(self.decks_dir, deck_name, "deck_data.json")
        
        if not os.path.exists(json_path): return {}

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)
            
            # Busca pelo nome exato
            for card_info in deck_data:
                if card_info.get("name") == card_name:
                    return card_info
            
            # Se não achou exato, tenta busca parcial (para resolver casos de apóstrofo no JSON)
            clean_search = self._sanitize_filename(card_name).lower()
            for card_info in deck_data:
                clean_json_name = self._sanitize_filename(card_info.get("name", "")).lower()
                if clean_search == clean_json_name:
                    return card_info
            
            return {}
        except Exception as e:
            print(f"Erro JSON {card_name}: {e}")
            return {}

    def baixar_deck_completo(self, deck_name, card_list, screen, font):
        """Baixa imagens e cria o JSON de dados."""
        path_deck = os.path.join(self.decks_dir, deck_name)
        os.makedirs(path_deck, exist_ok=True)
        
        data_collection = []
        total = len(card_list)
        
        for i, card_name in enumerate(card_list):
            # Renderiza status
            screen.fill((30, 30, 30))
            txt = font.render(f"Baixando: {card_name} ({i+1}/{total})", True, (255, 255, 255))
            screen.blit(txt, (screen.get_width()//2 - txt.get_width()//2, screen.get_height()//2))
            pygame.display.flip()

            # API Scryfall (Busca fuzzy para ser mais tolerante com nomes)
            # Usar 'fuzzy' em vez de 'exact' ajuda com acentos e pequenos erros
            url_search = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"
            
            try:
                resp = requests.get(url_search, timeout=5)
                if resp.status_code == 200:
                    card_data = resp.json()
                    
                    # Salva dados para o JSON
                    data_collection.append({
                        "name": card_name, # Salva com o nome que está na SUA lista (importante para o link funcionar)
                        "real_name": card_data.get("name"), # Nome oficial
                        "type_line": card_data.get("type_line", ""),
                        "mana_cost": card_data.get("mana_cost", ""),
                        "cmc": card_data.get("cmc", 0),
                        "oracle_text": card_data.get("oracle_text", "")
                    })

                    # Baixa a imagem
                    img_url = None
                    if "image_uris" in card_data:
                        img_url = card_data["image_uris"]["normal"]
                    elif "card_faces" in card_data:
                        img_url = card_data["card_faces"][0]["image_uris"]["normal"]
                    
                    if img_url:
                        # Salva a imagem com o nome exato da lista .txt para garantir o load
                        # Se tiver caractere invalido, removemos APENAS na hora de salvar o arquivo
                        safe_filename = self._sanitize_filename(card_name) + ".jpg"
                        self._download_image(img_url, path_deck, safe_filename)
                else:
                    print(f"Scryfall não achou: {card_name}")
            except Exception as e:
                print(f"Erro download {card_name}: {e}")

        # Salva o JSON
        with open(os.path.join(path_deck, "deck_data.json"), "w", encoding='utf-8') as f:
            json.dump(data_collection, f, indent=4)

    def _download_image(self, url, folder, filename):
        try:
            path_img = os.path.join(folder, filename)
            # Só baixa se não existir
            if not os.path.exists(path_img):
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(path_img, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
        except Exception as e:
            print(f"Erro ao salvar arquivo {filename}: {e}")
