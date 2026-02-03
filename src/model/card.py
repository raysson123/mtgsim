import pygame
import os
import re

class Card:
    def __init__(self, name, assets_mgr, nome_deck):
        self.name = name
        self.image = assets_mgr.get_card_image(nome_deck, name)
        self.rect = self.image.get_rect()
        
        # Dados do JSON
        data = assets_mgr.get_card_data(nome_deck, name)
        self.type_line = data.get("type_line", "")
        self.mana_cost_raw = data.get("mana_cost", "")
        self.cmc = data.get("cmc", 0)
        
        # --- NOVOS ATRIBUTOS PARA EFEITOS E ANEXOS ---
        self.oracle_text = data.get("oracle_text", "")  # Descrição das regras
        self.keywords = data.get("keywords", [])        # Ex: ['Haste', 'Flying']
        self.host_card = None  # Se for um equipamento/aura, indica em qual criatura está
        # ---------------------------------------------

        # Atributos de Estado
        self.tapped = False
        self.dragging = False
        self.is_hovered = False
        
        # Converte a string "{B}{1}" em um dicionário amigável
        self.mana_cost_dict = self._parse_mana_cost(self.mana_cost_raw)

    def _parse_mana_cost(self, mana_str):
        custo = {'white': 0, 'blue': 0, 'black': 0, 'red': 0, 'green': 0, 'colorless': 0, 'generic': 0}
        if not mana_str: return custo
        
        simbolos = re.findall(r'{(.*?)}', mana_str)
        for s in simbolos:
            s = s.upper()
            if s == 'W': custo['white'] += 1
            elif s == 'U': custo['blue'] += 1
            elif s == 'B': custo['black'] += 1
            elif s == 'R': custo['red'] += 1
            elif s == 'G': custo['green'] += 1
            elif s == 'C': custo['colorless'] += 1
            elif s.isdigit(): custo['generic'] += int(s)
        return custo

    @property
    def is_land(self):
        return "land" in self.type_line.lower()

    @property
    def is_instant(self):
        return "instant" in self.type_line.lower()

    def toggle_tap(self, force_untap=False):
        if force_untap:
            self.tapped = False
        else:
            self.tapped = not self.tapped
            
    def update_position(self, mouse_pos):
        if self.dragging:
            self.rect.center = mouse_pos
            # Ao arrastar manualmente, o equipamento se solta do host (opcional, regra do MTG)
            # self.host_card = None 
        elif self.host_card:
            # --- LÓGICA DE EMPILHAMENTO (OFFSET) ---
            # Deslocamento de 20% para a esquerda (negativo) e para cima (negativo)
            offset_x = self.rect.width * 0.20
            offset_y = self.rect.height * 0.20
            
            self.rect.x = self.host_card.rect.x - offset_x
            self.rect.y = self.host_card.rect.y - offset_y
        
    def draw(self, surface):
        img_final = self.image
        
        # Se estiver virada, rotaciona
        if self.tapped:
            img_final = pygame.transform.rotate(self.image, -90)
            rect_desenho = img_final.get_rect(center=self.rect.center)
        else:
            rect_desenho = self.rect

        # Se houver hover (e não estiver arrastando), amplia
        if self.is_hovered and not self.dragging:
            largura, altura = img_final.get_size()
            img_final = pygame.transform.smoothscale(img_final, (int(largura * 1.4), int(altura * 1.4)))
            rect_desenho = img_final.get_rect(center=self.rect.center)
            rect_desenho.y -= 60 

        surface.blit(img_final, rect_desenho)
