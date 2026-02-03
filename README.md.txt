/mtg_simulator
│
├── main.py                 # Ponto de entrada (inicializa o Pygame e o State Manager)
├── config.py               # Configurações globais (IP, Portas, Resolução, Cores)
│
├── /assets                 # Imagens, fontes e sons
│   ├── /cards              # Cache local das imagens baixadas da API
│   └── /ui                 # Elementos da interface (botões, fundos)
│
├── /decks                  # Arquivos .txt contendo as listas das cartas
│
├── /src
│   ├── /model              # Lógica pura do jogo (Independente de visual)
│   │   ├── card.py         # Classe da Carta
│   │   ├── player.py       # Classe do Jogador e Mão/Grimório/Cemitério
│   │   ├── game_logic.py   # Regras, Fases do Turno, Pilha (Stack)
│   │   └── bot.py          # Lógica de decisão para jogadores IA
│   │
│   ├── /view               # Renderização e Interface (Pygame)
│   │   ├── renderer.py     # Desenha o campo, cartas e efeitos
│   │   ├── menu_view.py    # UI do Menu Principal e Lobby
│   │   └── assets_mgr.py   # Gerencia download e carregamento da Scryfall
│   │
│   ├── /controller         # Input do usuário e comunicação
│   │   ├── input_handler.py# Captura cliques e teclado
│   │   └── network_mgr.py  # Cliente para envio/recebimento de dados
│   │
│   └── /network            # Scripts do Servidor
│       └── server.py       # Servidor centralizador de salas e mensagens
│
└── requirements.txt        # Dependências (pygame, requests, etc.)