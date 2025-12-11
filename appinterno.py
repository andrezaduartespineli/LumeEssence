from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'admin_secret_key'

# Configuração de Upload de Imagens
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    con = get_db()
    cur = con.cursor()
    # Busca 5 últimos pedidos
    try:
        cur.execute("""
            SELECT p.id_pedido, c.nome, p.status, p.valor_total 
            FROM tb_pedidos p
            JOIN tb_clientes c ON p.id_cliente = c.id_cliente
            ORDER BY p.data_pedido DESC LIMIT 5
        """)
        ultimos_pedidos = cur.fetchall()
    except:
        ultimos_pedidos = []
    con.close()
    return render_template("interno/dashboard.html", pedidos=ultimos_pedidos)

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
    nome = request.form.get("nome_produto")
    sku = request.form.get("sku")
    descricao = request.form.get("descricao")
    preco_custo = request.form.get("preco_custo")
    preco_venda = request.form.get("preco_venda")
    qtd_estoque = request.form.get("qtd_estoque")
    fornecedor = request.form.get("fornecedor")
    categoria_id = request.form.get("categoria_id")
    subcategoria_id = request.form.get("subcategoria_id")
    data_cad = request.form.get("data_cad") or datetime.now().strftime("%Y-%m-%d")
    
    # Tratamento da Imagem
    nome_imagem = "sem_foto.png"
    if 'img_produto' in request.files:
        file = request.files['img_produto']
        if file.filename != '':
            nome_imagem = file.filename
            # Salva na pasta
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO tb_produtos (nome_produto, sku, descricao, preco_custo, preco_venda, 
            qtd_estoque, fornecedor, categoria_id, subcategoria_id, img_produto, data_cad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, sku, descricao, preco_custo, preco_venda, qtd_estoque, fornecedor, categoria_id, subcategoria_id, nome_imagem, data_cad))
        con.commit()
    except Exception as e:
        print(f"Erro ao salvar produto: {e}")
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
    razao_social = request.form.get("razao_social")
    nome_fantasia = request.form.get("nome_fantasia")
    cnpj = request.form.get("cnpj")
    tel_cel = request.form.get("tel_cel")
    categoria = request.form.get("categoria")
    insc_estadual = request.form.get("insc_estadual", "")
    email = request.form.get("email")
    cep = request.form.get("cep")
    endereco = request.form.get("endereco")
    cidade = request.form.get("cidade")
    estado = request.form.get("estado")
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
    return render_template("interno/financeiro.html")

@app.route("/financeiro/receita/nova", methods=["POST"])
def nova_receita():
    descricao = request.form.get("descricao")
    valor = request.form.get("valor")
    data_emissao = request.form.get("data_emissao")
    data_venc = request.form.get("data_venc")
    categoria = request.form.get("categoria")
    status = request.form.get("status")

    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO tb_contasReceber (descricao, valor, data_emissao, data_venc, categoria, status) VALUES (?, ?, ?, ?, ?, ?)",
                (descricao, valor, data_emissao, data_venc, categoria, status))
    con.commit()
    con.close()
    return redirect("/financeiro")

@app.route("/financeiro/despesa/nova", methods=["POST"])
def nova_despesa():
    descricao = request.form.get("descricao")
    valor = request.form.get("valor")
    data_venc = request.form.get("data_venc")
    categoria = request.form.get("categoria")
    status = request.form.get("status")
    fornecedor = request.form.get("fornecedor")

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
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")
    data_nasc = request.form.get("data_nasc")
    tel_cel = request.form.get("tel_cel")
    email_pessoal = request.form.get("email_pessoal")
    cargo = request.form.get("cargo")
    departamento = request.form.get("departamento")
    email_login = request.form.get("email_login")
    senha = request.form.get("senha")
    permissao = request.form.get("permissao")
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

# --- Clientes ---
@app.route("/cliente.html")
@app.route("/cliente")
def clientes():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_clientes")
    clientes = cur.fetchall()
    con.close()
    return render_template("interno/cliente.html", clientes=clientes)

# --- Pedidos (Visualização Admin) ---
@app.route("/pedido.html")
@app.route("/pedidos")
def pedidos():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT p.id_pedido, c.nome, p.data_pedido, p.valor_total, p.status, p.forma_pagamento, p.parcelas
            FROM tb_pedidos p
            JOIN tb_clientes c ON p.id_cliente = c.id_cliente
            ORDER BY p.data_pedido DESC
        """)
        pedidos = cur.fetchall()
    except:
        pedidos = []
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
    app.run(debug=True, port=5001)