class AttachmentManager:
    def __init__(self):
        # Chave: Criatura (alvo) | Valor: Lista de Objetos (Equipamentos/Auras)
        self.links = {} 

    def attach(self, equipment, creature):
        """Vincula um equipamento a uma criatura e atualiza a posição visual."""
        # 1. Se o equipamento já estava em outra criatura, limpa o vínculo antigo
        self.detach_from_all(equipment)
        
        # 2. Registra o novo vínculo no dicionário
        if creature not in self.links:
            self.links[creature] = []
        
        self.links[creature].append(equipment)
        
        # 3. Informa à carta do equipamento quem é o seu novo hospedeiro (para o offset visual)
        equipment.host_card = creature
        
        print(f"[ATTACH] {equipment.name} -> {creature.name}")

    def detach_from_all(self, equipment):
        """Remove o equipamento de qualquer hospedeiro e limpa sua referência visual."""
        for creature in self.links:
            if equipment in self.links[creature]:
                self.links[creature].remove(equipment)
        
        # Limpa a referência no objeto Card para ele parar de seguir a criatura
        equipment.host_card = None

    def get_bonuses(self, creature):
        """Calcula o bônus total de P/T que uma criatura está recebendo."""
        extra_power = 0
        extra_toughness = 0
        
        items = self.links.get(creature, [])
        for item in items:
            text = (item.oracle_text or "").lower()
            # Lógica simples de busca por texto (Regex seria ideal aqui no futuro)
            if "gets +1/+1" in text:
                extra_power += 1
                extra_toughness += 1
            elif "gets +2/+0" in text:
                extra_power += 2
            elif "gets +2/+2" in text:
                extra_power += 2
                extra_toughness += 2
                
        return extra_power, extra_toughness

    def clean_invalid_links(self, battlefield):
        """
        Verifica se criaturas saíram de campo. 
        Se a criatura saiu, o equipamento fica no campo mas sem host.
        """
        updated_links = {}
        for creature, items in self.links.items():
            if creature in battlefield:
                # Se a criatura ainda está viva, mantemos os itens que também estão em campo
                valid_items = []
                for item in items:
                    if item in battlefield:
                        valid_items.append(item)
                    else:
                        item.host_card = None # Item saiu de campo (ex: destruído)
                
                if valid_items:
                    updated_links[creature] = valid_items
            else:
                # Se a criatura saiu de campo (morreu), todos os equipamentos dela perdem o host
                for item in items:
                    item.host_card = None
        
        self.links = updated_links
