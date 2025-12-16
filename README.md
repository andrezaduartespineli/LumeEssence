# 🕯️ Lume Essence - Ecossistema Full-Stack de E-commerce & ERP

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?style=for-the-badge&logo=flask&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-HTML5%2FCSS3%2FJS-green?style=for-the-badge&logo=html5&logoColor=white)

> .**Lume Essence** é uma solução web integrada que une uma Loja Virtual (B2C) moderna a um Sistema de Gestão (ERP) robusto. .Desenvolvido para gerenciar todo o ciclo de vida de uma marca de velas aromáticas e decoração, desde a captação do cliente até o controle financeiro.

---

## 🚀 Visão Geral do Projeto

O sistema foi arquitetado com separação de contextos para garantir segurança e organização:

### 🛍️ 1. Loja Virtual (Frente de Loja)
Focada na experiência do usuário (UX), com navegação fluida e design responsivo.
* .**Catálogo Dinâmico:** Listagem de produtos alimentada pelo banco de dados com filtros visuais por categoria e aroma.
* .**Checkout Progressivo:** Fluxo de compra moderno com identificação de usuário e carrinho persistente via Sessão.
* .**Simulação de Pagamento:** Interface visual interativa para Cartão de Crédito (com tokenização simulada) e Pix (com cálculo de desconto).
* .**Área do Cliente:** Painel completo para acompanhamento de pedidos (timeline de status), gestão de endereços e carteira digital.

### 📊 2. Painel Administrativo (ERP)
.Backoffice protegido para controle total da operação.
* .**Dashboard Financeiro:** KPIs em tempo real (Vendas Hoje, Estoque Baixo) e controle de fluxo de caixa (Receitas vs. Despesas).
* .**Gestão de Estoque:** CRUD completo de produtos com upload de imagens e controle de status.
* .**CRM e Equipe:** Gestão da base de clientes, fornecedores e controle de acesso de funcionários com níveis de permissão.
* .**Automação:** Ferramenta para importação em massa de produtos via planilha Excel/CSV.

---

## 🛠️ Stack Tecnológico

* .**Backend:** Python com Flask (Microframework).
    * .Arquitetura modular com aplicações separadas para Site (`appsite.py`) e Admin (`appinterno.py`).
    * .`Werkzeug` para segurança de senhas (Hash) e uploads.
* .**Banco de Dados:** SQLite relacional com modelagem otimizada para Pedidos, Itens, Financeiro e Estoque.
* **Frontend:**
    * .HTML5 Semântico com Jinja2 Templating.
    * .CSS3 Avançado (Grid, Flexbox, Variáveis e Responsividade).
    * .JavaScript Vanilla para máscaras de input, consumo de API (ViaCEP) e manipulação do DOM.

---

## 📂 Estrutura do Projeto

```text
LumeEssence/
├── appsite.py          # Aplicação da Loja (Porta 5000)
├── appinterno.py       # Aplicação do Admin (Porta 5001)
├── db_lume.db.py       # Script de criação do Banco de Dados
├── static/             # Arquivos estáticos (CSS, JS, Imagens)
│   ├── uploads/        # Imagens dinâmicas dos produtos/perfis
│   ├── viacep.js       # Integração com API de CEP
│   └── mascaras.js     # Formatação de inputs (CPF, Tel, Moeda)
└── templates/          # Templates HTML (Jinja2)
    ├── site/           # Páginas da Loja
    ├── interno/        # Páginas do Admin
    └── area_cliente/   # Painel do Usuário
```



# ⚡ Como Rodar o Projeto

## Pré-requisitos
Python 3.x instalado.

## Passo a Passo
Clone o repositório:

git clone [https://github.com/andrezaduartespineli/LumeEssence.git](https://github.com/andrezaduartespineli/LumeEssence.git)
cd LumeEssence


## Crie o Ambiente Virtual (Opcional, mas recomendado):
python -m venv .venv


### Windows:
.venv\Scripts\activate

### Linux/Mac:
source .venv/bin/activate


## Instale as dependências:
pip install flask


## Inicialize o Banco de Dados: Este comando criará o arquivo db_lume.db com todas as tabelas necessárias.
python db_lume.db.py


## Execute as Aplicações: O sistema roda em duas portas simultâneas. Abra dois terminais:

#### Terminal 1 (Loja):
python appsite.py
Acesse: http://127.0.0.1:5000

#### Terminal 2 (Admin):
python appinterno.py
Acesse: http://127.0.0.1:5001

---


✨ Funcionalidades em Destaque
🔒 Segurança e Dados
Tokenização Simulada: Implementação de boas práticas de PCI-DSS, onde dados sensíveis de cartão não são persistidos, apenas tokens e dados públicos (bandeira/final).

Hash de Senhas: Estrutura preparada para criptografia de credenciais de usuários.

🎨 UX/UI (Experiência do Usuário)
Design System: Uso consistente de paleta de cores (--gold, --primary) e tipografia.

Feedback Visual: Modais interativos, loaders de verificação de e-mail e estados de erro/sucesso em formulários.

👩‍💻 Autoras
