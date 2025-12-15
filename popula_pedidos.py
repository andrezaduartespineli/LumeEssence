import sqlite3
import random
from datetime import datetime, timedelta

# Conecta ao banco
con = sqlite3.connect("db_lume.db")
cur = con.cursor()

print("🔌 Conectado ao banco de dados...")

# ==========================================
# 1. CRIAR CLIENTES FICTÍCIOS
# ==========================================
clientes_fake = [
    ('Julia Ramos', 'julia@email.com', '111.222.333-44', 'Feminino', '(11) 99999-1111', '01001-000', 'Rua das Flores', '10', 'Apto 1', 'Centro', 'São Paulo', 'SP'),
    ('Pedro Santos', 'pedro@email.com', '222.333.444-55', 'Masculino', '(21) 98888-2222', '20000-000', 'Av. do Sol', '200', '', 'Copacabana', 'Rio de Janeiro', 'RJ'),
    ('Mariana Costa', 'mari@email.com', '333.444.555-66', 'Feminino', '(31) 97777-3333', '30000-000', 'Rua da Paz', '30', 'Casa', 'Savassi', 'Belo Horizonte', 'MG'),
    ('Lucas Oliveira', 'lucas@email.com', '444.555.666-77', 'Masculino', '(41) 96666-4444', '80000-000', 'Rua Verde', '45', '', 'Batel', 'Curitiba', 'PR'),
    ('Fernanda Lima', 'fer@email.com', '555.666.777-88', 'Feminino', '(51) 95555-5555', '90000-000', 'Av. Bento', '500', 'Bl 2', 'Moinhos', 'Porto Alegre', 'RS'),
    ('Rafael Souza', 'rafa@email.com', '666.777.888-99', 'Masculino', '(61) 94444-6666', '70000-000', 'SQN 202', 'Bl C', 'Apto 202', 'Asa Norte', 'Brasília', 'DF'),
    ('Beatriz Alves', 'bia@email.com', '777.888.999-00', 'Feminino', '(71) 93333-7777', '40000-000', 'Rua do Mar', '88', '', 'Barra', 'Salvador', 'BA'),
    ('Gustavo Dias', 'gus@email.com', '888.999.000-11', 'Masculino', '(81) 92222-8888', '50000-000', 'Rua Nova', '12', '', 'Boa Viagem', 'Recife', 'PE'),
    ('Camila Rocha', 'cams@email.com', '999.000.111-22', 'Feminino', '(85) 91111-9999', '60000-000', 'Av. Beira Mar', '1000', '1501', 'Meireles', 'Fortaleza', 'CE'),
    ('Bruno Martins', 'bru@email.com', '000.111.222-33', 'Masculino', '(92) 99999-0000', '69000-000', 'Rua Amazonas', '55', '', 'Centro', 'Manaus', 'AM')
]

print("👤 Cadastrando clientes...")
try:
    for c in clientes_fake:
        # Senha padrão hash (123456)
        senha_padrao = "pbkdf2:sha256:600000$SomeSalt$..." 
        cur.execute("""
            INSERT INTO tb_clientes (nome, email, cpf, genero, tel_cel, cep, endereco, n, complemento, bairro, cidade, estado, senha, confirmar_senha, data_cad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], '123', '123'))
except Exception as e:
    print(f"Nota: Alguns clientes já existiam ou deram erro: {e}")

# ==========================================
# 2. GERAR PEDIDOS
# ==========================================

# Busca IDs necessários
cur.execute("SELECT id_cliente FROM tb_clientes")
ids_clientes = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id_produto, preco_venda FROM tb_produtos")
produtos = cur.fetchall() # Lista de tuplas (id, preco)

if not produtos:
    print("❌ ERRO: Você precisa ter produtos cadastrados! Importe a planilha primeiro.")
    exit()

print(f"📦 Gerando pedidos com base em {len(produtos)} produtos e {len(ids_clientes)} clientes...")

status_opcoes = ['Pendente', 'Pago', 'Separando', 'Enviado', 'Entregue', 'Cancelado']
pagamento_opcoes = ['credit', 'pix']

try:
    for i in range(25): # Gerar 25 pedidos
        
        # Sorteia dados do pedido
        cliente_id = random.choice(ids_clientes)
        status_pedido = random.choices(status_opcoes, weights=[10, 20, 15, 20, 30, 5], k=1)[0]
        pagamento = random.choice(pagamento_opcoes)
        parcelas = random.randint(1, 3) if pagamento == 'credit' else 1
        
        # Data aleatória nos últimos 30 dias
        dias_atras = random.randint(0, 30)
        data_pedido = datetime.now() - timedelta(days=dias_atras)
        
        # Cria o pedido (Valor 0 inicial)
        cur.execute("""
            INSERT INTO tb_pedidos (id_cliente, data_pedido, status, valor_total, data_entrega, forma_pagamento, parcelas)
            VALUES (?, ?, ?, 0, ?, ?, ?)
        """, (cliente_id, data_pedido, status_pedido, data_pedido + timedelta(days=5), pagamento, parcelas))
        
        id_pedido = cur.lastrowid
        total_pedido = 0

        # Adiciona 1 a 5 itens no pedido
        qtd_itens = random.randint(1, 5)
        produtos_selecionados = random.sample(produtos, min(qtd_itens, len(produtos)))

        for prod in produtos_selecionados:
            id_prod = prod[0]
            preco = prod[1]
            qtd = random.randint(1, 3)
            subtotal = preco * qtd
            
            # Insere Item
            cur.execute("""
                INSERT INTO tb_itensPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (id_pedido, id_prod, qtd, preco, subtotal))
            
            total_pedido += subtotal

        # Atualiza o valor total do pedido
        cur.execute("UPDATE tb_pedidos SET valor_total = ? WHERE id_pedido = ?", (total_pedido, id_pedido))

        # ==========================================
        # 3. LANÇAR NO FINANCEIRO
        # ==========================================
        if status_pedido != 'Cancelado':
            status_fin = 'Recebido' if status_pedido in ['Pago', 'Separando', 'Enviado', 'Entregue'] else 'Pendente'
            cur.execute("""
                INSERT INTO tb_contasReceber (descricao, valor, data_emissao, data_venc, categoria, status, id_pedido, id_cliente)
                VALUES (?, ?, ?, ?, 'Venda Online', ?, ?, ?)
            """, (f"Pedido #{id_pedido} - Site", total_pedido, data_pedido, data_pedido, status_fin, id_pedido, cliente_id))

    con.commit()
    print("\n🚀 Sucesso! 25 Pedidos gerados e financeiro atualizado.")

except Exception as e:
    print(f"Erro ao gerar pedidos: {e}")
    con.rollback()

finally:
    con.close()