# 🕯️ Lume Essence - Ecossistema Full-Stack de E-commerce & ERP

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?style=for-the-badge&logo=flask&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-HTML5%2FCSS3%2FJS-green?style=for-the-badge&logo=html5&logoColor=white)

> .**Lume Essence** é uma solução web integrada que une uma Loja Virtual (B2C) moderna a um Sistema de Gestão (ERP) robusto[cite: 7]. .Desenvolvido para gerenciar todo o ciclo de vida de uma marca de velas aromáticas e decoração, desde a captação do cliente até o controle financeiro[cite: 7].

---

## 🚀 Visão Geral do Projeto

O sistema foi arquitetado com separação de contextos para garantir segurança e organização:

### 🛍️ 1. Loja Virtual (Frente de Loja)
Focada na experiência do usuário (UX), com navegação fluida e design responsivo.
* .**Catálogo Dinâmico:** Listagem de produtos alimentada pelo banco de dados com filtros visuais por categoria e aroma[cite: 9].
* .**Checkout Progressivo:** Fluxo de compra moderno com identificação de usuário e carrinho persistente via Sessão[cite: 10, 11].
* .**Simulação de Pagamento:** Interface visual interativa para Cartão de Crédito (com tokenização simulada) e Pix (com cálculo de desconto)[cite: 12, 13].
* .**Área do Cliente:** Painel completo para acompanhamento de pedidos (timeline de status), gestão de endereços e carteira digital[cite: 13].

### 📊 2. Painel Administrativo (ERP)
.Backoffice protegido para controle total da operação[cite: 14].
* .**Dashboard Financeiro:** KPIs em tempo real (Vendas Hoje, Estoque Baixo) e controle de fluxo de caixa (Receitas vs. Despesas)[cite: 15].
* .**Gestão de Estoque:** CRUD completo de produtos com upload de imagens e controle de status[cite: 16].
* .**CRM e Equipe:** Gestão da base de clientes, fornecedores e controle de acesso de funcionários com níveis de permissão[cite: 17, 18].
* .**Automação:** Ferramenta para importação em massa de produtos via planilha Excel/CSV.

---

## 🛠️ Stack Tecnológico

* .**Backend:** Python com Flask (Microframework)[cite: 19].
    * .Arquitetura modular com aplicações separadas para Site (`appsite.py`) e Admin (`appinterno.py`)[cite: 19].
    * .`Werkzeug` para segurança de senhas (Hash) e uploads[cite: 90].
* .**Banco de Dados:** SQLite relacional com modelagem otimizada para Pedidos, Itens, Financeiro e Estoque[cite: 20].
* **Frontend:**
    * .HTML5 Semântico com Jinja2 Templating[cite: 21].
    * .CSS3 Avançado (Grid, Flexbox, Variáveis e Responsividade)[cite: 21].
    * .JavaScript Vanilla para máscaras de input, consumo de API (ViaCEP) e manipulação do DOM[cite: 22].

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

# 📦 Importação em Massa de Produtos (Excel)

Para agilizar o cadastro de estoque, o projeto conta com um script de automação que lê uma planilha Excel e insere os produtos diretamente no banco de dados.

### Pré-requisitos
#### Instale as bibliotecas de manipulação de dados:

pip install pandas openpyxl

```bash
Como Usar
#Crie a Planilha: Na pasta raiz do projeto, crie um arquivo Excel chamado:
novos_produtos.xlsx.

#Preencha os Dados: A primeira linha deve conter exatamente os nomes das colunas do banco. 

Exemplo: nome_produto,sku,descricao,preco_custo,preco_venda,qtd_estoque,fornecedor,categoria
Vela Lavanda,VEL-001,Vela aromática,15.00,45.00,100,Próprio,Velas Aromáticas

#Execute o Script: Rode o comando abaixo no terminal:
python importar_lote.py

✅ O sistema identificará automaticamente as colunas, definirá imagens padrão e inserirá os registros.

```


✨ Funcionalidades em Destaque
🔒 Segurança e Dados
Tokenização Simulada: Implementação de boas práticas de PCI-DSS, onde dados sensíveis de cartão não são persistidos, apenas tokens e dados públicos (bandeira/final).

Hash de Senhas: Estrutura preparada para criptografia de credenciais de usuários.

🎨 UX/UI (Experiência do Usuário)
Design System: Uso consistente de paleta de cores (--gold, --primary) e tipografia.

Feedback Visual: Modais interativos, loaders de verificação de e-mail e estados de erro/sucesso em formulários.

👩‍💻 Autoras
