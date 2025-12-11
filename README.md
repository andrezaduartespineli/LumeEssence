Markdown

# 🕯️ Lume Essence - Ecossistema Full-Stack de E-commerce & ERP

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?style=for-the-badge&logo=flask&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-HTML5%2FCSS3%2FJS-green?style=for-the-badge&logo=html5&logoColor=white)

> **Lume Essence** é uma solução web integrada que une uma Loja Virtual (B2C) moderna a um Sistema de Gestão (ERP) robusto. Desenvolvido para gerenciar todo o ciclo de vida de uma marca de velas aromáticas e decoração, desde a captação do cliente até o controle financeiro.

---

## 🚀 Visão Geral do Projeto

O sistema foi arquitetado com separação de contextos para garantir segurança e organização:

### 🛍️ 1. Loja Virtual (Frente de Loja)
Focada na experiência do usuário (UX), com navegação fluida e design responsivo.
* **Catálogo Dinâmico:** Listagem de produtos alimentada pelo banco de dados com filtros visuais.
* **Checkout Progressivo:** Fluxo de compra moderno (semelhante aos grandes marketplaces) que identifica o usuário pelo e-mail antes de solicitar cadastro.
* **Carrinho Inteligente:** Gerenciamento de itens via Sessão (Session) do Flask, permitindo persistência durante a navegação.
* **Simulação de Pagamento:**
    * **Cartão de Crédito:** Interface visual interativa e simulação de **Tokenização** (salvamento seguro apenas dos últimos 4 dígitos).
    * **Pix:** Cálculo automático de descontos.
* **Área do Cliente:** Histórico de pedidos com timeline de status, carteira digital e gestão de endereços.

### 📊 2. Painel Administrativo (ERP)
Backoffice para controle total da operação.
* **Dashboard Financeiro:** Visão de fluxo de caixa com gráficos e tabelas de Receitas vs. Despesas.
* **Gestão de Estoque:** CRUD completo de produtos com upload de imagens e controle de status (Ativo/Inativo).
* **CRM e Equipe:** Gestão de base de clientes e controle de acesso de funcionários.
* **Cadeia de Suprimentos:** Cadastro e gestão de fornecedores categorizados.

---

## 🛠️ Stack Tecnológico

* **Backend:** Python com Flask (Microframework). Utiliza arquitetura modular com dois pontos de entrada (`appsite.py` e `appinterno.py`).
* **Banco de Dados:** SQLite relacional. Estrutura otimizada com tabelas para Pedidos, Itens, Clientes, Financeiro e Estoque.
* **Frontend:**
    * HTML5 Semântico com Jinja2 Templating.
    * CSS3 Avançado (Grid, Flexbox, Variáveis `:root` e Responsividade).
    * JavaScript Vanilla (Sem frameworks pesados) para manipulação do DOM e Fetch API.

---

## 📂 Estrutura do Projeto

```text
LumeEssence/
├── appsite.py          # Aplicação da Loja (Porta 5000)
├── appinterno.py       # Aplicação do Admin (Porta 5001)
├── db_lume.db.py       # Script de modelagem e criação do Banco
├── static/             # Arquivos estáticos
│   ├── uploads/        # Imagens dos produtos (geradas dinamicamente)
│   ├── styleinterno.css
│   ├── stylesite.css
│   └── ...
└── templates/          # Templates HTML (Jinja2)
    ├── site/           # Páginas da Loja (Home, Checkout, Login)
    ├── interno/        # Páginas do Admin (Dashboard, Cadastros)
    └── area_cliente/   # Páginas logadas do usuário 
```



## ⚡ Como Rodar o Projeto

# Pré-requisitos
Python 3.x instalado.

# Passo a Passo
Clone o repositório:

git clone [https://github.com/andrezaduartespineli/LumeEssence.git](https://github.com/andrezaduartespineli/LumeEssence.git)
cd LumeEssence


# Crie o Ambiente Virtual (Opcional, mas recomendado):
python -m venv .venv


## Windows:
.venv\Scripts\activate

## Linux/Mac:
source .venv/bin/activate


# Instale as dependências:
pip install flask


# Inicialize o Banco de Dados: Este comando criará o arquivo db_lume.db com todas as tabelas necessárias.
python db_lume.db.py


# Execute as Aplicações: O sistema roda em duas portas simultâneas. Abra dois terminais:

# Terminal 1 (Loja):
python appsite.py
Acesse: http://127.0.0.1:5000

# Terminal 2 (Admin):
python appinterno.py
Acesse: http://127.0.0.1:5001




✨ Funcionalidades em Destaque
🔒 Segurança e Dados
Tokenização Simulada: Implementação de boas práticas de PCI-DSS, onde dados sensíveis de cartão não são persistidos, apenas tokens e dados públicos (bandeira/final).

Hash de Senhas: Estrutura preparada para criptografia de credenciais de usuários.

🎨 UX/UI (Experiência do Usuário)
Design System: Uso consistente de paleta de cores (--gold, --primary) e tipografia.

Feedback Visual: Modais interativos, loaders de verificação de e-mail e estados de erro/sucesso em formulários.

👩‍💻 Autoras
