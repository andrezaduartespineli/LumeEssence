import sqlite3 as sql

#Criar a conexão com o banco de dados (ou criar o banco se não existir)
con = sql.connect ('db_lume.db')
cur = con.cursor()

#Tabela Produtos
cur.execute('DROP TABLE IF EXISTS tb_produtos')

sql_produto = '''CREATE TABLE "tb_produtos" (
    "id_produto" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome_produto" VARCHAR(45) NOT NULL,
    "sku" VARCHAR(45) NOT NULL,
    "descricao" VARCHAR(100) NOT NULL,
    "preco_custo" DECIMAL(10,2) NOT NULL,
    "preco_venda" DECIMAL(10,2) NOT NULL,
    "qtd_estoque" INTEGER NOT NULL,
    "fornecedor" VARCHAR(45) NOT NULL,
    "categoria_id" INTEGER NOT NULL,
    "subcategoria_id" INTEGER NOT NULL,
    "img_produto" BLOB DEFAULT NULL,
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_produto)

#Tabela Categorias
cur.execute('DROP TABLE IF EXISTS tb_categorias')

sql_categoria = '''CREATE TABLE "tb_categorias" (
    "id_categoria" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome_categoria" VARCHAR(45) NOT NULL,
    "descricao" VARCHAR(100) NOT NULL,
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_categoria)

#Tabela Subcategorias
cur.execute('DROP TABLE IF EXISTS tb_subcategorias')

sql_subcategoria = '''CREATE TABLE "tb_subcategorias" (
    "id_subcategoria" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome_subcategoria" VARCHAR(45) NOT NULL,
    "descricao" VARCHAR(100) NOT NULL,
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_subcategoria)

#Tabela Clientes
cur.execute('DROP TABLE IF EXISTS tb_clientes')

sql_cliente = '''CREATE TABLE "tb_clientes" (
    "id_cliente" INTEGER PRIMARY KEY AUTOINCREMENT,
    "cpf" BIGINT NOT NULL,
    "nome" VARCHAR(45) NOT NULL,
    "data_nasc" DATETIME NOT NULL,
    "genero" VARCHAR(45) NOT NULL,
    "nome_social" VARCHAR(45) DEFAULT NULL,
    "tel_cel" BIGINT NOT NULL,
    "email" VARCHAR(45) NOT NULL,
    "cep" int NOT NULL,
    "logradouro" VARCHAR(45) NOT NULL,
    "n" int NOT NULL,
    "complemento" VARCHAR(100) DEFAULT NULL,
    "referencia" VARCHAR(100) DEFAULT NULL,
    "bairro" VARCHAR(45) NOT NULL,
    "cidade" VARCHAR(45) NOT NULL,
    "estado" VARCHAR(2) NOT NULL,
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_cliente)

#Tabela Clientes Promoção
cur.execute('DROP TABLE IF EXISTS tb_clientesPromo')

sql_clientePromo = '''CREATE TABLE "tb_clientesPromo" (
    "id_clientepromo" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(45) NOT NULL,
    "email" VARCHAR(45) NOT NULL,
    "tel_cel" BIGINT NOT NULL,
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_clientePromo)

#Tabela Pedidos
cur.execute('DROP TABLE IF EXISTS tb_pedidos')

sql_pedido = '''CREATE TABLE "tb_pedidos" (
    "id_pedido" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_cliente" INTEGER NOT NULL,
    "data_pedido" DATETIME NOT NULL,
    "status" VARCHAR(20) NOT NULL,
    "valor_total" DECIMAL(10,2) NOT NULL,
    "data_entrega" DATETIME NOT NULL,
    "forma_pagamento" VARCHAR(20) NOT NULL
    )'''

cur.execute(sql_pedido)

#Tabela ItensPedido
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

#Tabela Fornecedores
cur.execute('DROP TABLE IF EXISTS tb_fornecedores')

sql_fornecedores = '''CREATE TABLE "tb_fornecedores" (
    "id_fornecedor" INTEGER PRIMARY KEY AUTOINCREMENT,
    "razao_social" VARCHAR(45) NOT NULL,
    "nome_fantasia" VARCHAR(45) NOT NULL,
    "cnpj" VARCHAR(45) NOT NULL,
    "tel_cel" VARCHAR(45) NOT NULL,
    "categoria" VARCHAR(100) NOT NULL,
    "insc_estadual" VARCHAR(20) DEFAULT NULL,
    "email" VARCHAR(45) NOT NULL,
    "cep" int NOT NULL,
    "endereco" VARCHAR(200) NOT NULL,
    "cidade" VARCHAR(45) NOT NULL,
    "estado" VARCHAR(2) NOT NULL,
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_fornecedores)

#Tabela ContasReceber
cur.execute('DROP TABLE IF EXISTS tb_contasReceber')

sql_contasReceber = '''CREATE TABLE "tb_contasReceber" (
    "id_contaReceber" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_cliente" INTEGER NOT NULL,
    "id_pedido" INTEGER NOT NULL,
    "descricao" VARCHAR(100) NOT NULL,
    "valor" DECIMAL(10,2) NOT NULL,
    "data_emissao" DATETIME NOT NULL,
    "data_venc" DATETIME NOT NULL,
    "status" VARCHAR(20) NOT NULL
    )'''

cur.execute(sql_contasReceber)

#Tabela Contatos
cur.execute('DROP TABLE IF EXISTS tb_contatos')

sql_contato = '''CREATE TABLE "tb_contatos" (
    "id_contato" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(45) NOT NULL,
    "email" VARCHAR(45) NOT NULL,
    "tel_cel" BIGINT NOT NULL,
    "mensagem" VARCHAR(255) NOT NULL,
    "data_contato" DATETIME NOT NULL
    )'''

cur.execute(sql_contato)

#Salvar as alterações e fechar a conexão
con.commit()
con.close()