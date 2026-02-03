import re

class EffectEngine:
    
    @staticmethod
    def process_etb(card, player):
        """Processa efeitos de 'Enters The Battlefield' (ETB)."""
        text = card.oracle_text.lower() if card.oracle_text else ""
        
        # 1. Tap Lands
        if "enters the battlefield tapped" in text or "enters tapped" in text:
            print(f"EFETIVADO: {card.name} entrou virado.")
            card.tapped = True

        # 2. Gain Lands
        if "gain 1 life" in text and ("enters the battlefield" in text or "enters" in text):
            print(f"EFETIVADO: Ganho de vida por {card.name}.")
            player.change_life(1)

    @staticmethod
    def trigger_activated_ability(card, player, assets_mgr, nome_deck, turn_mgr, attachment_mgr):
        """
        Processa habilidades ativadas. Agora verifica e cobra custos de mana.
        """
        text = card.oracle_text.lower() if card.oracle_text else ""

        # --- 1. Habilidade de EQUIPAR (Artefatos) ---
        if "equip" in text:
            # Tenta encontrar o custo, ex: "equip {1}" ou "equip {2}{w}"
            # Regex captura tudo que está entre chaves logo após a palavra equip
            match = re.search(r'equip\s*((?:\{[\w\d]+\})+)', text)
            
            custo_str = match.group(1) if match else "{0}"
            
            # Se tiver custo, tenta pagar
            if EffectEngine._pay_mana_cost(player, custo_str):
                # Callback: Só executa se o pagamento for bem sucedido
                def callback_equip(origem, alvo, p, a_mgr):
                    if "creature" in (alvo.type_line or "").lower():
                        a_mgr.attach(origem, alvo)
                        print(f"SISTEMA: {origem.name} equipada em {alvo.name}.")
                    else:
                        print("ALVO INVÁLIDO: Equipamentos só em criaturas.")

                EffectEngine.iniciar_selecao_alvo(card, player, turn_mgr, callback_equip)
            else:
                print(f"MANA INSUFICIENTE: Custo para equipar é {custo_str.upper()}")
            return

        # --- 2. Habilidade de SACRIFÍCIO (Busca/Compra) ---
        if "sacrifice" in text:
            # Ex: Commander's Sphere - "{T}, Sacrifice..."
            # Nota: Aqui poderíamos adicionar checagem de custo de mana se necessário
            
            if "draw a card" in text:
                if card in player.battlefield:
                    player.battlefield.remove(card)
                    player.grave.append(card)
                    player.draw(assets_mgr, 1, nome_deck)
                    attachment_mgr.detach_from_all(card)
                    print(f"EFETIVADO: {card.name} sacrificado para comprar carta.")
                    return
            
            if "search" in text:
                EffectEngine.resolve_evolving_wilds(card, player, assets_mgr, nome_deck, attachment_mgr)
                return

        # --- 3. Artefatos de Mana (Sol Ring, etc) ---
        if "{t}: add" in text and not card.tapped:
            if "{c}{c}" in text:
                player.mana_pool['colorless'] += 2
                print(f"DEBUG: {card.name} gerou 2 mana incolor.")
            else:
                player.mana_pool['colorless'] += 1 # Default genérico
                print(f"DEBUG: {card.name} gerou 1 mana.")
            card.tapped = True
            return

    @staticmethod
    def _pay_mana_cost(player, cost_str):
        """
        Tenta pagar o custo de mana especificado na string (ex: '{1}', '{B}{1}').
        Retorna True se pagou, False se não teve mana.
        """
        # Parsing simples do custo
        custo = {'white': 0, 'blue': 0, 'black': 0, 'red': 0, 'green': 0, 'colorless': 0, 'generic': 0}
        
        simbolos = re.findall(r'{(.*?)}', cost_str)
        for s in simbolos:
            s = s.upper()
            if s == 'W': custo['white'] += 1
            elif s == 'U': custo['blue'] += 1
            elif s == 'B': custo['black'] += 1
            elif s == 'R': custo['red'] += 1
            elif s == 'G': custo['green'] += 1
            elif s == 'C': custo['colorless'] += 1
            elif s.isdigit(): custo['generic'] += int(s)
            
        # Verifica Mana Colorida/Incolor específica primeiro
        temp_pool = player.mana_pool.copy() # Cópia para simular pagamento
        
        for color in ['white', 'blue', 'black', 'red', 'green', 'colorless']:
            if temp_pool[color] >= custo[color]:
                temp_pool[color] -= custo[color]
            else:
                return False # Falta mana colorida específica
        
        # Verifica Mana Genérica (pode ser paga com qualquer sobra)
        total_sobra = sum(temp_pool.values())
        if total_sobra >= custo['generic']:
            # Paga o genérico (priorizando incolor, depois o resto)
            generic_needed = custo['generic']
            
            # 1. Gasta incolor sobrando
            gasto_incolor = min(temp_pool['colorless'], generic_needed)
            temp_pool['colorless'] -= gasto_incolor
            generic_needed -= gasto_incolor
            
            # 2. Gasta qualquer outra cor para o restante do genérico
            for color in ['white', 'blue', 'black', 'red', 'green']:
                if generic_needed <= 0: break
                gasto = min(temp_pool[color], generic_needed)
                temp_pool[color] -= gasto
                generic_needed -= gasto
            
            # Efetiva a transação no player real
            player.mana_pool = temp_pool
            print(f"Pagamento realizado: {cost_str}")
            return True
            
        return False

    @staticmethod
    def iniciar_selecao_alvo(card_origem, player, turn_mgr, callback):
        print(f"MODO ALVO: Selecione o objetivo para {card_origem.name}")
        turn_mgr.modo_selecao = True
        turn_mgr.origem_alvo = card_origem
        turn_mgr.callback_alvo = callback

    @staticmethod
    def finalizar_selecao_alvo(alvo, player, turn_mgr, attachment_mgr):
        if turn_mgr.callback_alvo:
            turn_mgr.callback_alvo(turn_mgr.origem_alvo, alvo, player, attachment_mgr)
            
        turn_mgr.modo_selecao = False
        turn_mgr.origem_alvo = None
        turn_mgr.callback_alvo = None

    @staticmethod
    def resolve_evolving_wilds(card, player, assets_mgr, nome_deck, attachment_mgr):
        # Lógica Evolving Wilds (sem alterações)
        if card in player.battlefield:
            player.battlefield.remove(card)
            player.grave.append(card)
            attachment_mgr.detach_from_all(card)
            
            terreno_nome = None
            indice_na_lib = -1
            basicos = ["plains", "island", "swamp", "mountain", "forest"]
            
            for i, nome_carta_lib in enumerate(player.library):
                if any(b in nome_carta_lib.lower() for b in basicos):
                    terreno_nome = nome_carta_lib
                    indice_na_lib = i
                    break
            
            if terreno_nome:
                player.library.pop(indice_na_lib)
                from src.model.card import Card
                nova_land = Card(terreno_nome, assets_mgr, nome_deck)
                nova_land.tapped = True 
                player.battlefield.append(nova_land)
                player.shuffle()
                print(f"Busca concluída: {terreno_nome} em jogo (virado).")
