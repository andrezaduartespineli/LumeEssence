from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'admin_secret_key'

# Configuração de Upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Cria a pasta se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db():
    conn = sqlite3.connect("db_lume.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Dashboard ---
@app.route("/")
@app.route("/dashboard.html")
def dashboard():
    # Aqui você pode adicionar SQLs para contar vendas, total financeiro, etc.
    return render_template("interno/dashboard.html")

# --- Produtos ---
@app.route("/produto.html")
@app.route("/produtos")
def listar_produtos():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_produtos")
    produtos = cur.fetchall()
    con.close()
    return render_template("interno/produto.html", produtos=produtos)

@app.route("/cad_produtos.html")
def view_cad_produto():
    return render_template("interno/cad_produtos.html")

@app.route("/produto/novo", methods=["POST"])
def produto_novo():
    nome = request.form["nome_produto"]
    sku = request.form["sku"]
    descricao = request.form["descricao"]
    preco_custo = request.form["preco_custo"]
    preco_venda = request.form["preco_venda"]
    qtd_estoque = request.form["qtd_estoque"]
    fornecedor = request.form["fornecedor"]
    categoria_id = request.form["categoria_id"]
    subcategoria_id = request.form["subcategoria_id"]
    data_cad = request.form["data_cad"] or datetime.now().strftime("%Y-%m-%d")
    
    # Tratamento do Tamanho (Concatenando na descrição)
    tamanho_extra = request.form.get("tamanho_extra", "")
    if tamanho_extra:
        descricao = f"{descricao} - Tamanho: {tamanho_extra}"

    # Upload da Imagem
    nome_imagem = "sem_foto.png" # Padrão
    if 'img_produto' in request.files:
        file = request.files['img_produto']
        if file.filename != '':
            nome_imagem = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO tb_produtos (nome_produto, sku, descricao, preco_custo, preco_venda, 
        qtd_estoque, fornecedor, categoria_id, subcategoria_id, img_produto, data_cad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, sku, descricao, preco_custo, preco_venda, qtd_estoque, fornecedor, categoria_id, subcategoria_id, nome_imagem, data_cad))
    
    con.commit()
    con.close()
    return redirect("/produtos")

# --- Fornecedores ---
@app.route("/fornecedores.html")
@app.route("/fornecedores")
def listar_fornecedores():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_fornecedores")
    dados = cur.fetchall()
    con.close()
    return render_template("interno/fornecedores.html", fornecedores=dados)

@app.route("/novo-fornecedor.html")
def view_novo_fornecedor():
    return render_template("interno/novo-fornecedor.html")

@app.route("/novo-fornecedor", methods=["POST"])
def novo_fornecedor_post():
    razao_social = request.form["razao_social"]
    nome_fantasia = request.form["nome_fantasia"]
    cnpj = request.form["cnpj"]
    tel_cel = request.form["tel_cel"]
    categoria = request.form["categoria"]
    insc_estadual = request.form.get("insc_estadual", "")
    email = request.form["email"]
    cep = request.form["cep"]
    endereco = request.form["endereco"]
    cidade = request.form["cidade"]
    estado = request.form["estado"]
    data_cad = datetime.now()

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO tb_fornecedores (razao_social, nome_fantasia, cnpj, tel_cel, categoria, 
        insc_estadual, email, cep, endereco, cidade, estado, data_cad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (razao_social, nome_fantasia, cnpj, tel_cel, categoria, insc_estadual, email, cep, endereco, cidade, estado, data_cad))
    con.commit()
    con.close()
    return redirect("/fornecedores")

# --- Financeiro ---
@app.route("/financeiro.html")
@app.route("/financeiro")
def financeiro():
    # Aqui você poderia buscar os dados do banco para preencher a tabela
    return render_template("interno/financeiro.html")

@app.route("/financeiro/receita/nova", methods=["POST"])
def nova_receita():
    descricao = request.form["descricao"]
    valor = request.form["valor"]
    data_emissao = request.form.get("data_emissao")
    data_venc = request.form["data_venc"]
    categoria = request.form["categoria"]
    status = request.form["status"]

    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO tb_contasReceber (descricao, valor, data_emissao, data_venc, categoria, status) VALUES (?, ?, ?, ?, ?, ?)",
                (descricao, valor, data_emissao, data_venc, categoria, status))
    con.commit()
    con.close()
    return redirect("/financeiro")

@app.route("/financeiro/despesa/nova", methods=["POST"])
def nova_despesa():
    descricao = request.form["descricao"]
    valor = request.form["valor"]
    data_venc = request.form["data_venc"]
    categoria = request.form["categoria"]
    status = request.form["status"]
    fornecedor = request.form["fornecedor"]

    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO tb_despesas (descricao, valor, data_venc, categoria, status, fornecedor) VALUES (?, ?, ?, ?, ?, ?)",
                (descricao, valor, data_venc, categoria, status, fornecedor))
    con.commit()
    con.close()
    return redirect("/financeiro")

# --- Funcionários ---
@app.route("/funcionarios.html")
@app.route("/funcionarios")
def funcionarios():
    con = get_db()
    cur = con.cursor()
    # Verifica se a tabela existe antes de consultar
    try:
        cur.execute("SELECT * FROM tb_funcionarios")
        dados = cur.fetchall()
    except:
        dados = []
    con.close()
    return render_template("interno/funcionarios.html", funcionarios=dados)

@app.route("/novo-funcionario.html")
def view_novo_funcionario():
    return render_template("interno/novo-funcionario.html")

@app.route("/funcionario/novo", methods=["POST"])
def novo_funcionario_post():
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    data_nasc = request.form["data_nasc"]
    tel_cel = request.form["tel_cel"]
    email_pessoal = request.form["email_pessoal"]
    cargo = request.form["cargo"]
    departamento = request.form["departamento"]
    email_login = request.form["email_login"]
    senha = request.form["senha"]
    permissao = request.form["permissao"]
    
    ativo = 1 if request.form.get("ativo") else 0

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO tb_funcionarios (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, ativo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, ativo))
    con.commit()
    con.close()
    return redirect("/funcionarios")

# --- Outras Rotas ---
@app.route("/cliente.html")
@app.route("/cliente")
def clientes():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_clientes")
    clientes = cur.fetchall()
    con.close()
    return render_template("interno/cliente.html", clientes=clientes)

@app.route("/pedido.html")
@app.route("/pedidos")
def pedidos():
    con = get_db()
    cur = con.cursor()
    # Busca pedidos com nome do cliente
    cur.execute("""
        SELECT p.id_pedido, c.nome, p.data_pedido, p.valor_total, p.status, p.forma_pagamento, p.parcelas
        FROM tb_pedidos p
        JOIN tb_clientes c ON p.id_cliente = c.id_cliente
        ORDER BY p.data_pedido DESC
    """)
    pedidos = cur.fetchall()
    con.close()
    return render_template("interno/pedido.html", pedidos=pedidos)

@app.route("/configuracoes.html")
@app.route("/configuracoes")
def configuracoes():
    return render_template("interno/configuracoes.html")

@app.route("/login.html")
def login():
    return render_template("interno/login.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001) # Roda na porta 5001 para não conflitar com o site