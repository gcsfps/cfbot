# Automação Segura para Gerenciar "Melhores Amigos" no Instagram

## Objetivo
Criar um sistema de automação em Python que colete todos os seguidores de uma conta do Instagram e adicione-os à lista de "Melhores Amigos". O sistema é otimizado para contas grandes com foco em velocidade e segurança.

## Estrutura do Projeto
### Arquivos
- `main.py`: Código principal para controle da automação
- `utils.py`: Funções auxiliares (manipulação de arquivos CSV e logs)
- `config.json`: Arquivo para configurar parâmetros
- `requirements.txt`: Dependências do projeto
- `logs/`: Diretório para logs
- `data/`: Diretório para controle de progresso e checkpoints

### Sistema de Controle de Progresso
- Checkpoint automático a cada 100 usuários processados
- Arquivo de controle para retomar de onde parou
- Sistema de backup dos usuários já processados

## Instalação e Configuração Rápida
1. Clone o repositório
2. Execute: `pip install -r requirements.txt`
3. Configure o `config.json` com suas preferências
4. Execute: `python main.py`

## Monitoramento
- Log em tempo real do progresso
- Contagem de usuários processados/restantes
- Status de execução e velocidade média

## Tratamento de Erros
- Reconexão automática em caso de falhas
- Retomada do último checkpoint
- Sistema de retry em caso de falhas temporárias

## Boas Práticas
- Recomendado usar IPs dedicados
- Sistema otimizado para processamento em massa
- Checkpoints frequentes para segurança dos dados

## Recursos de Segurança
1. Simulação de Comportamento Humano
2. Respeito a Limites Naturais
3. Rotação de IPs
4. Detecção de Bloqueios
5. Armazenamento Seguro
6. Atualização Frequente
