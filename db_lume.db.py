import sqlite3 as sql

# Criar a conexão com o banco de dados
con = sql.connect('db_lume.db')
cur = con.cursor()

# ==========================================
# 1. TABELAS DO E-COMMERCE (SITE)
# ==========================================

# Tabela Newsletter (Leads) - NOVO
cur.execute('DROP TABLE IF EXISTS tb_newsletter')
sql_newsletter = '''CREATE TABLE "tb_newsletter" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(100),
    "whatsapp" VARCHAR(20),
    "email" VARCHAR(100),
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
cur.execute(sql_newsletter)

# Tabela Clientes
cur.execute('DROP TABLE IF EXISTS tb_clientes')
sql_cliente = '''CREATE TABLE "tb_clientes" (
    "id_cliente" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(100) NOT NULL,
    "data_nasc" DATE NOT NULL,
    "cpf" VARCHAR(14) NOT NULL,
    "genero" VARCHAR(20),
    "tel_cel" VARCHAR(20) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "cep" VARCHAR(9) NOT NULL,
    "endereco" VARCHAR(100) NOT NULL,
    "n" VARCHAR(10) NOT NULL,
    "complemento" VARCHAR(50),
    "referencia" VARCHAR(100),
    "bairro" VARCHAR(50) NOT NULL,
    "cidade" VARCHAR(50) NOT NULL,
    "estado" VARCHAR(2) NOT NULL,
    "senha" VARCHAR(100) NOT NULL,
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
cur.execute(sql_cliente)

# Tabela Cartões (Tokenização Simulada) - NOVO
cur.execute('DROP TABLE IF EXISTS tb_cartoes')
sql_cartoes = '''CREATE TABLE "tb_cartoes" (
    "id_cartao" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_cliente" INTEGER NOT NULL,
    "nome_titular" VARCHAR(100) NOT NULL,
    "ultimos_4" VARCHAR(4) NOT NULL,
    "bandeira" VARCHAR(20) NOT NULL,
    "token_pagamento" VARCHAR(100) NOT NULL, 
    "validade" VARCHAR(5) NOT NULL,
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
cur.execute(sql_cartoes)

# Tabela Pedidos - ATUALIZADO (Com Parcelas)
cur.execute('DROP TABLE IF EXISTS tb_pedidos')
sql_pedido = '''CREATE TABLE "tb_pedidos" (
    "id_pedido" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_cliente" INTEGER NOT NULL,
    "data_pedido" DATETIME NOT NULL,
    "status" VARCHAR(20) NOT NULL,
    "valor_total" DECIMAL(10,2) NOT NULL,
    "data_entrega" DATETIME,
    "forma_pagamento" VARCHAR(20) NOT NULL,
    "parcelas" INTEGER DEFAULT 1
    )'''
cur.execute(sql_pedido)

# Tabela Itens do Pedido
cur.execute('DROP TABLE IF EXISTS tb_itensPedido')
sql_itensPedido = '''CREATE TABLE "tb_itensPedido" (
    "id_itemPedido" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_pedido" INTEGER NOT NULL,
    "id_produto" INTEGER NOT NULL,
    "quantidade" INTEGER NOT NULL,
    "preco_unitario" DECIMAL(10,2) NOT NULL,
    "subtotal" DECIMAL(10,2) NOT NULL
    )'''
cur.execute(sql_itensPedido)

# Tabela Contatos (Fale Conosco)
cur.execute('DROP TABLE IF EXISTS tb_contatos')
sql_contato = '''CREATE TABLE "tb_contatos" (
    "id_contato" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "tel_cel" VARCHAR(20) NOT NULL,
    "mensagem" TEXT NOT NULL,
    "data_contato" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
cur.execute(sql_contato)


# ==========================================
# 2. TABELAS DO ADMIN (ERP)
# ==========================================

# Tabela Produtos (Atualizada com Categoria, Aroma, Tamanho e Ativo)
cur.execute('DROP TABLE IF EXISTS tb_produtos')
sql_produto = '''CREATE TABLE "tb_produtos" (
    "id_produto" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome_produto" VARCHAR(100) NOT NULL,
    "sku" VARCHAR(20),
    "descricao" TEXT,
    "preco_custo" DECIMAL(10,2),
    "preco_venda" DECIMAL(10,2),
    "qtd_estoque" INTEGER,
    "fornecedor" VARCHAR(100),
    "categoria" VARCHAR(50), 
    "aroma" VARCHAR(50),
    "tamanho" VARCHAR(50),
    "img_produto" VARCHAR(255),
    "ativo" BOOLEAN DEFAULT 1,
    "data_cad" DATETIME
    )'''
# Obs: "categoria" agora é VARCHAR para aceitar textos como "Velas Aromáticas" vindos do HTML
cur.execute(sql_produto)

# Tabela Funcionários
cur.execute('DROP TABLE IF EXISTS tb_funcionarios')
sql_funcionarios = '''CREATE TABLE "tb_funcionarios" (
    "id_funcionario" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(100) NOT NULL,
    "cpf" VARCHAR(14),
    "data_nasc" DATE,
    "tel_cel" VARCHAR(20),
    "email_pessoal" VARCHAR(100),
    "cargo" VARCHAR(50),
    "departamento" VARCHAR(50),
    "email_login" VARCHAR(100) NOT NULL,
    "senha" VARCHAR(100) NOT NULL,
    "permissao" VARCHAR(20) NOT NULL,
    "foto" VARCHAR(255),  
    "ativo" BOOLEAN DEFAULT 1,
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
cur.execute(sql_funcionarios)

# Tabela Fornecedores
cur.execute('DROP TABLE IF EXISTS tb_fornecedores')
sql_fornecedores = '''CREATE TABLE "tb_fornecedores" (
    "id_fornecedor" INTEGER PRIMARY KEY AUTOINCREMENT,
    "razao_social" VARCHAR(100) NOT NULL,
    "nome_fantasia" VARCHAR(100) NOT NULL,
    "cnpj" VARCHAR(20) NOT NULL,
    "tel_cel" VARCHAR(20),
    "categoria" VARCHAR(50),
    "insc_estadual" VARCHAR(20),
    "email" VARCHAR(100) NOT NULL,
    "cep" VARCHAR(9) NOT NULL,
    "endereco" VARCHAR(200) NOT NULL,
    "cidade" VARCHAR(50) NOT NULL,
    "estado" VARCHAR(2) NOT NULL,
    "data_cad" DATETIME
    )'''
cur.execute(sql_fornecedores)

# Tabela Contas a Receber (Financeiro Entradas) - ATUALIZADO
cur.execute('DROP TABLE IF EXISTS tb_contasReceber')
sql_contasReceber = '''CREATE TABLE "tb_contasReceber" (
    "id_contaReceber" INTEGER PRIMARY KEY AUTOINCREMENT,
    "descricao" VARCHAR(100) NOT NULL,
    "valor" DECIMAL(10,2) NOT NULL,
    "data_emissao" DATE,
    "data_venc" DATE NOT NULL,
    "categoria" VARCHAR(50),
    "status" VARCHAR(20) NOT NULL,
    "id_cliente" INTEGER, 
    "id_pedido" INTEGER
    )'''
cur.execute(sql_contasReceber)

# Tabela Despesas (Financeiro Saídas) - NOVO
cur.execute('DROP TABLE IF EXISTS tb_despesas')
sql_despesas = '''CREATE TABLE "tb_despesas" (
    "id_despesa" INTEGER PRIMARY KEY AUTOINCREMENT,
    "descricao" VARCHAR(100) NOT NULL,
    "valor" DECIMAL(10,2) NOT NULL,
    "data_venc" DATE NOT NULL,
    "categoria" VARCHAR(50),
    "status" VARCHAR(20) NOT NULL,
    "fornecedor" VARCHAR(100),
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''
cur.execute(sql_despesas)

# Tabelas Auxiliares (Categorias) - Mantidas
cur.execute('DROP TABLE IF EXISTS tb_categorias')
sql_categoria = '''CREATE TABLE "tb_categorias" (
    "id_categoria" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome_categoria" VARCHAR(45) NOT NULL
    )'''
cur.execute(sql_categoria)

cur.execute('DROP TABLE IF EXISTS tb_subcategorias')
sql_subcategoria = '''CREATE TABLE "tb_subcategorias" (
    "id_subcategoria" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome_subcategoria" VARCHAR(45) NOT NULL
    )'''
cur.execute(sql_subcategoria)

# Salvar e Fechar
con.commit()
con.close()

print("Banco de dados db_lume.db atualizado com sucesso!")