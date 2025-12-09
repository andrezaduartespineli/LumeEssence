# CRUD Flask (SQLite)

Este projeto é um CRUD simples em Flask usando SQLite.

## Como rodar

Pré-requisitos: Python 3.9+.


### Windows (PowerShell)

```powershell

# 1- instalar o Python
# 2 - Instalar o  VS Code

python -m venv .venv # 3 - criar ambiente virtual

.venv/scripts/activate # 4 - Ativar ambiente virtual

pip install flask # 5 - Instalar o Flask

python db_smarteventos.py   # 6 - cria/zera o banco db_smarteventos.db

python app.py       # 7 - Rodar o software - inicia o servidor

# Obs: Para parar o servidor CTRL + C
```
Acesse em <http://127.0.0.1:5000>


# Se a ativação da venv for bloqueada, abra o PowerShell e execute:

```powershell

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

```

### Windows (Prompt de Comando - CMD)

python -m venv .venv
.venv\scripts\activate
pip install flask
python smartevenos.py   # cria/zera o banco
python app.py       # inicia o servidor

```

Para parar o servidor: CTRL+C. 

Para sair da venv: `deactivate`.

 
## Observações
 
- O log 404 para `/favicon.ico` é esperado se não houver um favicon configurado e não afeta o funcionamento.
