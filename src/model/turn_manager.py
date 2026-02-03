class TurnManager:
    def __init__(self):
        # Ordem das fases do Magic
        self.fases = [
            "UNTAP", "UPKEEP", "DRAW", 
            "MAIN 1", 
            "BEGIN COMBAT", "DECLARE ATTACKERS", "DECLARE BLOCKERS", "DAMAGE", "END COMBAT", 
            "MAIN 2", 
            "END STEP", "CLEANUP"
        ]
        self.fase_atual_idx = 0
        
        # --- [ATRIBUTOS DE ESTADO DO JOGO] ---
        self.quantidade_mulligans = 0
        self.em_mulligan = True  # O jogo começa na fase de decisão de mão

        # --- [SISTEMA DE ALVOS / SELEÇÃO] ---
        self.modo_selecao = False    # Indica se o jogo está esperando um clique de alvo
        self.origem_alvo = None      # A carta que disparou a necessidade de um alvo
        self.callback_alvo = None    # A função (efeito) que será executada ao confirmar o alvo

    def get_fase_atual(self):
        return self.fases[self.fase_atual_idx]

    def proxima_fase(self, jogador, assets_mgr, nome_deck):
        """Avança as fases e pula automaticamente as etapas burocráticas."""
        if self.em_mulligan:
            print("Decida o Mulligan antes de prosseguir.")
            return

        # Se estivermos em modo de seleção de alvo, bloqueamos a mudança de fase 
        # para evitar bugs de regras (opcional, mas recomendado)
        if self.modo_selecao:
            print(f"Defina o alvo para {self.origem_alvo.name} antes de mudar de fase!")
            return

        # Avança para a próxima
        self.fase_atual_idx += 1
        
        # Se passar do Cleanup (última fase), volta para o Untap do próximo turno
        if self.fase_atual_idx >= len(self.fases):
            self.fase_atual_idx = 0
            
        fase = self.get_fase_atual()

        # --- LÓGICA DE SALTO AUTOMÁTICO (Início do Turno) ---
        if fase == "UNTAP":
            print(">>> Automatizando: Untap Step")
            jogador.untap_all()
            jogador.mana_pool = {cor: 0 for cor in jogador.mana_pool}
            self.proxima_fase(jogador, assets_mgr, nome_deck)
            return

        if fase == "UPKEEP":
            print(">>> Automatizando: Upkeep Step")
            self.proxima_fase(jogador, assets_mgr, nome_deck)
            return

        if fase == "DRAW":
            print(">>> Automatizando: Draw Step")
            jogador.draw(assets_mgr, 1, nome_deck)
            self.proxima_fase(jogador, assets_mgr, nome_deck)
            return

        # --- LÓGICA DE SALTO AUTOMÁTICO (Fim do Turno) ---
        if fase == "CLEANUP":
            print(">>> Automatizando: Cleanup Step")
            if len(jogador.hand) > 7:
                print(f"Atenção: Você tem {len(jogador.hand)} cartas. Precisa descartar.")
            else:
                self.proxima_fase(jogador, assets_mgr, nome_deck)
                return

        print(f"--- AGUARDANDO JOGADOR: {fase} ---")

    def finalizar_mulligan(self):
        """Encerra a fase de mulligan e permite o início do jogo."""
        self.em_mulligan = False
        print("Mão mantida! O jogo começou.")

    def registrar_mulligan(self):
        """Incrementa o contador de mulligans."""
        self.quantidade_mulligans += 1

    def reset_turn(self):
        self.fase_atual_idx = 0
