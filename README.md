# Qulotto

Qulotto é um projeto de estudo que tenta gerar palpites para a Lotofácil usando diferentes abordagens:

- aleatória
- estatística
- vetor de intencionalidade
- inspirada em computação quântica
- simulador quântico leve

O objetivo principal não é prometer acerto de loteria. O objetivo é estudar:

- modelagem de dados
- backtest
- comparação de estratégias
- ideias de computação quântica aplicadas de forma experimental

## Aviso Importante

Este projeto é educacional e experimental.

Ele **não garante prêmio**, **não prevê o futuro** e **não deve ser tratado como recomendação financeira**.

## O Que o Projeto Faz

O sistema consegue:

- baixar e armazenar histórico da Lotofácil
- comparar estratégias diferentes
- rodar backtests com relatórios e gráficos
- gerar palpites para concursos futuros com base no histórico disponível

## Como Rodar

## Atualize os Dados Antes

Antes de rodar `run.sh` ou `run.bat`, atualize o banco de dados local com os concursos mais recentes.

### Linux e macOS

```bash
./atualizar.sh
```

### Windows

```bat
atualizar.bat
```

Esses scripts:

1. garantem Python 3.12
2. preparam o `.venv`
3. instalam o `requirements.txt`
4. executam o coletor em [`src/scripts/001_fetch.py`](/home/gc/dev/ai/qulotto/src/scripts/001_fetch.py)

Depois disso, use `run.sh` ou `run.bat`.

Se preferir interface gráfica no navegador, use `gui.sh` ou `gui.bat`.

### Linux e macOS

Use:

```bash
./run.sh
```

Para gerar palpites para um concurso futuro:

```bash
./run.sh --future --qtd 10
```

Para abrir a interface gráfica:

```bash
./gui.sh
```

Para abrir a interface gráfica em um navegador específico:

```bash
./gui.sh --browser firefox
```

### Windows

Use:

```bat
run.bat
```

Para gerar palpites para um concurso futuro:

```bat
run.bat --future --qtd 10
```

Para abrir a interface gráfica:

```bat
gui.bat
```

## O Que Esses Scripts Fazem

Os arquivos `run.sh` e `run.bat` tentam:

1. encontrar o Python 3.12
2. instalar o Python 3.12, se necessário
3. criar o ambiente `.venv`
4. instalar as dependências do `requirements.txt`
5. rodar o projeto com os argumentos que você passar

Os arquivos `atualizar.sh` e `atualizar.bat` fazem o mesmo bootstrap, mas executam a atualização do histórico antes do uso do sistema.

Os arquivos `gui.sh` e `gui.bat` fazem o mesmo bootstrap e depois sobem um servidor local com interface HTML + JavaScript para você escolher os argumentos sem usar terminal.

## Exemplos de Uso

Backtest simples:

```bash
./atualizar.sh
./run.sh --qtd 5 --inicio 100 --fim 120
```

Bateria completa:

```bash
./atualizar.sh
./run.sh --completo
```

Previsão para o próximo concurso:

```bash
./atualizar.sh
./run.sh --future --qtd 10
```

No Windows, troque `./atualizar.sh` por `atualizar.bat` e `./run.sh` por `run.bat`.

## Onde Ficam os Resultados

Os resultados são salvos em:

[`docs/report/`](/home/gc/dev/ai/qulotto/docs/report)

Você vai encontrar arquivos como:

- relatórios em Markdown
- arquivos JSON
- arquivos CSV
- gráficos em PNG
- palpites para concursos futuros

## Estrutura do Projeto

- [`main.py`](/home/gc/dev/ai/qulotto/main.py): ponto de entrada
- [`src/data/`](/home/gc/dev/ai/qulotto/src/data): leitura e persistência de dados
- [`src/strategies/`](/home/gc/dev/ai/qulotto/src/strategies): estratégias de geração de palpites
- [`src/evaluation/`](/home/gc/dev/ai/qulotto/src/evaluation): backtest, relatórios e gráficos
- [`src/quantum_inspired/`](/home/gc/dev/ai/qulotto/src/quantum_inspired): infraestrutura da estratégia inspirada em quantum
- [`src/quantum/`](/home/gc/dev/ai/qulotto/src/quantum): simulador quântico leve do projeto

## Licença

Este projeto usa a licença MIT.

Veja o arquivo [`LICENSE`](/home/gc/dev/ai/qulotto/LICENSE).
