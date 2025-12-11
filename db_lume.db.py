import sqlite3 as sql

#Criar a conexão com o banco de dados (ou criar o banco se não existir)
con = sql.connect ('db_lume.db')
cur = con.cursor()

#Tabela Produtos ok
cur.execute('DROP TABLE IF EXISTS tb_produtos')

sql_produto = '''CREATE TABLE "tb_produtos" (
    "id_produto" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome_produto" VARCHAR(45) NOT NULL,
    "fornecedor" VARCHAR(45) NOT NULL,
    "categoria" INTEGER NOT NULL,
    "aroma" VARCHAR(45) NOT NULL,
    "tamanho" VARCHAR(45) NOT NULL,
    "sku" VARCHAR(45) NOT NULL,
    "qtd_estoque" INTEGER NOT NULL,
    "preco_custo" DECIMAL(10,2) NOT NULL,
    "preco_venda" DECIMAL(10,2) NOT NULL,
    "data_cad" DATETIME NOT NULL,
    "descricao" VARCHAR(100) NOT NULL,
    "img_produto" BLOB DEFAULT NULL
    )'''

cur.execute(sql_produto)

#Tabela Clientes ok
cur.execute('DROP TABLE IF EXISTS tb_clientes')

sql_cliente = '''CREATE TABLE "tb_clientes" (
    "id_cliente" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(45) NOT NULL,
    "data_nasc" DATETIME NOT NULL,
    "cpf" BIGINT NOT NULL,
    "genero" VARCHAR(45) NOT NULL,
    "tel_cel" BIGINT NOT NULL,
    "email" VARCHAR(45) NOT NULL,
    "cep" int NOT NULL,
    "endereco" VARCHAR(45) NOT NULL,
    "n" int NOT NULL,
    "complemento" VARCHAR(100) DEFAULT NULL,
    "referencia" VARCHAR(100) DEFAULT NULL,
    "bairro" VARCHAR(45) NOT NULL,
    "cidade" VARCHAR(45) NOT NULL,
    "estado" VARCHAR(2) NOT NULL,
    "senha" VARCHAR(100) NOT NULL,
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_cliente)

# Tabela de Newsletter (Leads) ok
cur.execute('DROP TABLE IF EXISTS tb_newsletter')

sql_newsletter = '''CREATE TABLE "tb_newsletter" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(100),
    "whatsapp" VARCHAR(20),
    "email" VARCHAR(100),
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''

cur.execute(sql_newsletter)

#Tabela Pedidos ok
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

#Tabela ItensPedido x
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

#Tabela Fornecedores ok
cur.execute('DROP TABLE IF EXISTS tb_fornecedores')

sql_fornecedores = '''CREATE TABLE "tb_fornecedores" (
    "id_fornecedor" INTEGER PRIMARY KEY AUTOINCREMENT,
    "razao_social" VARCHAR(45) NOT NULL,
    "nome_fantasia" VARCHAR(45) NOT NULL,
    "cnpj" VARCHAR(45) NOT NULL,
    "insc_estadual" VARCHAR(20) DEFAULT NULL,
    "categoria" VARCHAR(100) NOT NULL,
    "nome_repre" VARCHAR(45) NOT NULL,
    "tel_cel" VARCHAR(45) NOT NULL,
    "email" VARCHAR(45) NOT NULL,
    "cep" int NOT NULL,
    "endereco" VARCHAR(200) NOT NULL,
    "cidade" VARCHAR(45) NOT NULL,
    "estado" VARCHAR(2) NOT NULL,
    "observacao" VARCHAR(100) NOT NULL, 
    "data_cad" DATETIME NOT NULL
    )'''

cur.execute(sql_fornecedores)

# Tabela Funcionários ok
cur.execute('DROP TABLE IF EXISTS tb_funcionarios')

sql_funcionarios = '''CREATE TABLE "tb_funcionarios" (
    "id_funcionario" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nome" VARCHAR(100) NOT NULL,
    "cpf" VARCHAR(14) NOT NULL,
    "data_nasc" DATE NOT NULL,
    "tel_cel" VARCHAR(20) NOT NULL,
    "email_pessoal" VARCHAR(100) NOT NULL,
    "cep" int NOT NULL,
    "endereco" VARCHAR(45) NOT NULL,
    "bairro" VARCHAR(45) NOT NULL,
    "cidade" VARCHAR(45) NOT NULL,
    "estado" VARCHAR(2) NOT NULL,
    "cargo" VARCHAR(50) NOT NULL,
    "departamento" VARCHAR(50) NOT NULL,
    "email_login" VARCHAR(100) NOT NULL,
    "senha" VARCHAR(100) NOT NULL,
    "permissao" VARCHAR(20) NOT NULL,
    "ativo" BOOLEAN DEFAULT 1,
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''

cur.execute(sql_funcionarios)


#Tabela ContasReceber ok
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

# --- Tabela Despesas (Contas a Pagar) --- ok
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

#Tabela Contatos ok
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

# Tabela de Cartões (Tokenizados) ok
cur.execute('DROP TABLE IF EXISTS tb_cartoes')

sql_cartoes = '''CREATE TABLE "tb_cartoes" (
    "id_cartao" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_cliente" INTEGER NOT NULL,
    "nome_titular" VARCHAR(100) NOT NULL,
    "ultimos_4" VARCHAR(4) NOT NULL,
    "bandeira" VARCHAR(20) NOT NULL,
    "token_pagamento" VARCHAR(100) NOT NULL, 
    "validade" VARCHAR(5) NOT NULL,
    "parcelas" INTEGER DEFAULT 1,
    "data_cad" DATETIME DEFAULT CURRENT_TIMESTAMP
    )'''

# token_pagamento: Aqui ficaria o ID que o banco (Stripe/Pagar.me) te devolve.
# Vamos gerar um falso apenas para simular.
# Adicione isso no seu arquivo de banco ou execute num script separado
# Se for recriar a tabela do zero, adicione "parcelas INTEGER DEFAULT 1" na criação

cur.execute(sql_cartoes)

#Salvar as alterações e fechar a conexão
con.commit()
con.close()