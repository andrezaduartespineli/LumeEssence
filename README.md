# 🕯️ Lume Essence - Plataforma Full-Stack de E-commerce & Gestão

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Frontend](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-green)

> **Lume Essence** é uma aplicação web completa desenvolvida para gerenciar o ciclo de vida de uma marca de velas aromáticas e decoração. O projeto implementa um ecossistema duplo: uma **Loja Virtual (B2C)** focada na experiência do cliente e um **Painel Administrativo (ERP)** para controle operacional.

---

## 📸 Visão Geral

O sistema resolve a necessidade de centralizar vendas e gestão, eliminando processos manuais e oferecendo uma experiência de compra fluida.

### 🛒 Área do Cliente (Storefront)
Uma interface imersiva e responsiva para o consumidor final.
- **Catálogo Interativo:** Carrosséis de produtos, filtros por categoria (Velas, Home Spray, Kits) e detalhes técnicos.
- **Checkout Inteligente:**
  - **Identificação Progressiva:** Verifica e-mail antes de pedir cadastro completo (UX otimizada).
  - **Simulação de Pagamento:** Opções de Cartão de Crédito (com tokenização simulada e parcelamento) e Pix.
- **Área Logada:**
  - **Minha Carteira:** Gestão de cartões salvos (exibição segura apenas dos últimos 4 dígitos).
  - **Meus Pedidos:** Rastreamento visual de status (Timeline) e histórico de compras.
  - **Favoritos e Endereços:** Gestão completa de dados pessoais.

### 📊 Painel Administrativo (Backoffice)
Um ERP robusto para controle total da operação.
- **Dashboard Financeiro:** Visão de fluxo de caixa (Receitas vs. Despesas) com lançamentos categorizados.
- **Gestão de Produtos:** CRUD completo com upload de imagens, controle de estoque e variação de preços (Custo x Venda).
- **Cadeia de Suprimentos:** Gestão de fornecedores e controle de compras.
- **CRM e Equipe:** Base de clientes e controle de acesso de funcionários com níveis de permissão.

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python & Flask:** Arquitetura modular com rotas separadas para contextos de Admin e Loja.
- **SQLite:** Banco de dados relacional para persistência de dados.
- **Werkzeug:** Gerenciamento seguro de uploads de arquivos.

### Frontend
- **HTML5 & CSS3:** - Layouts responsivos utilizando **CSS Grid** e **Flexbox**.
  - Design System próprio com variáveis CSS (`:root`) para consistência visual.
- **JavaScript (Vanilla):** - Manipulação avançada do DOM para modais, cálculos de carrinho em tempo real e validações de formulário.
  - Comunicação assíncrona (Fetch API) para verificação de e-mail e dados dinâmicos.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Python 3.x instalado.

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/andrezaduartespineli/LumeEssence.git](https://github.com/andrezaduartespineli/LumeEssence.git)
   cd LumeEssence


# Crie e ative o ambiente virtual (Recomendado
   # Windows:
python -m venv .venv
.venv\Scripts\activate

# Instale as dependências
pip install flask 

# Inicialize o Banco de Dados
python db_lume.db.py

# Terminal 1 (Loja Virtual)
python appsite.py
# Acessar em: [http://127.0.0.1:5000](http://127.0.0.1:5000)

# Terminal 2 (Painel Admin):
python appinterno.py
# Acessar em: [http://127.0.0.1:5001](http://127.0.0.1:5001)

LumeEssence/
├── appsite.py          # Controlador da Loja (Frontend do Cliente)
├── appinterno.py       # Controlador do Admin (ERP Interno)
├── db_lume.db.py       # Script de criação/reset do Banco de Dados
├── static/             # Arquivos estáticos (CSS, JS, Imagens, Uploads)
│   ├── area-cliente.css
│   ├── styleinterno.css
│   ├── stylesite.css
│   ├── scriptinterno.js
│   ├── scriptsite.js
│   └── uploads/        # Imagens de produtos carregadas pelo sistema
└── templates/          # Arquivos HTML (Jinja2)
    ├── site/           # Páginas públicas (Home, Produto, Checkout)
    ├── area_cliente/   # Área logada do usuário
    └── interno/        # Telas do sistema administrativo