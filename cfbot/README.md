# Instagram Close Friends Bot

Uma extensão Chrome para automatizar a gestão da lista de "Melhores Amigos" no Instagram.

## Funcionalidades

- 🔄 Exportar lista de seguidores para CSV
- 👥 Adicionar seguidores automaticamente à lista de "Melhores Amigos"
- ⚡ Interface amigável e intuitiva
- 🛡️ Sistema anti-detecção integrado
- ⚙️ Configurações personalizáveis para maior segurança

## Requisitos

- Python 3.8+
- Google Chrome
- Selenium WebDriver
- Flask

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/gcsfps/cfbot.git
cd cfbot
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale a extensão no Chrome:
   - Abra chrome://extensions/
   - Ative o "Modo do desenvolvedor"
   - Clique em "Carregar sem compactação"
   - Selecione a pasta `extension` do projeto

## Configuração

1. Abra o Instagram no Chrome e faça login na sua conta
2. Configure os parâmetros de segurança na extensão:
   - Tamanho do lote (10-100)
   - Intervalo entre ações (0.1-2 segundos)
   - Pausa a cada X ações

## Uso

1. Clique no ícone da extensão na barra do Chrome
2. Escolha uma das opções:
   - "Exportar Seguidores": Salva a lista em CSV
   - "Adicionar aos Melhores Amigos": Adiciona automaticamente

## Recursos de Segurança

- Delays aleatórios entre ações
- Pausas automáticas para evitar bloqueios
- Uso do perfil atual do Chrome
- Headers e User-Agent personalizados
- Desativação de flags de automação

## Estrutura do Projeto

```
cfbot/
├── extension/               # Extensão Chrome
│   ├── manifest.json       # Configuração da extensão
│   ├── popup.html         # Interface da extensão
│   └── popup.js          # Lógica da interface
├── main.py                # Lógica principal do bot
├── server.py             # Servidor Flask
├── utils.py             # Funções utilitárias
└── requirements.txt    # Dependências Python
```

## Desenvolvimento

- Backend: Python com Flask e Selenium
- Frontend: HTML, CSS e JavaScript
- Comunicação: API REST com CORS habilitado
- Automação: Chrome WebDriver com anti-detecção

## Limitações

- Funciona apenas com o Chrome
- Requer login manual no Instagram
- Pode ser afetado por mudanças na interface do Instagram

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Segurança

⚠️ Use com moderação e respeito aos limites do Instagram para evitar bloqueios.

## Status do Projeto

🟢 Em desenvolvimento ativo
- [x] Exportação de seguidores
- [x] Adição aos melhores amigos
- [x] Interface básica
- [ ] Melhorias na interface
- [ ] Mais opções de configuração
