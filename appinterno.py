from flask import Flask, render_template, request, redirect
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "admin_secret_key"

# Upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_PATH = 'db_lume.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
@app.route('/dashboard.html')
def dashboard():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT p.id_pedido, c.nome, p.status, p.valor_total, p.data_pedido
            FROM tb_pedidos p
            LEFT JOIN tb_clientes c ON p.id_cliente = c.id_cliente
            ORDER BY p.data_pedido DESC
            LIMIT 5
        """)
        pedidos = cur.fetchall()
    except sqlite3.Error:
        pedidos = []
    finally:
        con.close()
    return render_template('interno/dashboard.html', pedidos=pedidos)


@app.route('/produto.html')
@app.route('/produtos')
def listar_produtos():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM tb_produtos')
        produtos = cur.fetchall()
    except sqlite3.Error:
        produtos = []
    finally:
        con.close()
    return render_template('interno/produto.html', produtos=produtos)


@app.route('/cad_produtos.html')
def view_cad_produto():
    return render_template('interno/cad_produtos.html')


@app.route('/produto/novo', methods=['POST'])
def produto_novo():
    nome = request.form.get('nome_produto', '')
    fornecedor = request.form.get('fornecedor', '')
    categoria = request.form.get('categoria', '')
    aroma = request.form.get('aroma', '')
    tamanho = request.form.get('tamanho', '')
    sku = request.form.get('sku', '')
    qtd_estoque = request.form.get('qtd_estoque') or 0
    preco_custo = request.form.get('preco_custo') or 0
    preco_venda = request.form.get('preco_venda') or 0
    data_cad = request.form.get('data_cad') or datetime.now().strftime('%Y-%m-%d')
    descricao = request.form.get('descricao', '')

    nome_imagem = 'sem_foto.png'
    if 'img_produto' in request.files:
        f = request.files['img_produto']
        if f and f.filename:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nome_imagem = filename

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO tb_produtos (nome_produto, fornecedor, categoria, aroma, tamanho, sku, qtd_estoque, preco_custo, preco_venda, data_cad, descricao, img_produto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, fornecedor, categoria, aroma, tamanho, sku, qtd_estoque, preco_custo, preco_venda, data_cad, descricao, nome_imagem))
        con.commit()
    except sqlite3.Error:
        con.rollback()
    finally:
        con.close()
    return redirect('/produtos')


@app.route('/fornecedores.html')
@app.route('/fornecedores')
def listar_fornecedores():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM tb_fornecedores')
        fornecedores = cur.fetchall()
    except sqlite3.Error:
        fornecedores = []
    finally:
        con.close()
    return render_template('interno/fornecedores.html', fornecedores=fornecedores)


@app.route('/novo-fornecedor.html')
def view_novo_fornecedor():
    return render_template('interno/novo-fornecedor.html')


@app.route('/novo-fornecedor', methods=['POST'])
def novo_fornecedor_post():
    razao_social = request.form.get('razao_social', '')
    nome_fantasia = request.form.get('nome_fantasia', '')
    cnpj = request.form.get('cnpj', '')
    tel_cel = request.form.get('tel_cel', '')
    categoria = request.form.get('categoria', '')
    insc_estadual = request.form.get('insc_estadual', '')
    email = request.form.get('email', '')
    cep = request.form.get('cep', '')
    endereco = request.form.get('endereco', '')
    cidade = request.form.get('cidade', '')
    estado = request.form.get('estado', '')
    nome_repre = request.form.get('nome_repre', '')
    observacao = request.form.get('observacao', '')
    data_cad = datetime.now()

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO tb_fornecedores (razao_social, nome_fantasia, cnpj, insc_estadual, categoria, nome_repre, tel_cel, email, cep, endereco, cidade, estado, observacao, data_cad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (razao_social, nome_fantasia, cnpj, insc_estadual, categoria, nome_repre, tel_cel, email, cep, endereco, cidade, estado, observacao, data_cad))
        con.commit()
    except sqlite3.Error:
        con.rollback()
    finally:
        con.close()
    return redirect('/fornecedores')


@app.route('/financeiro.html')
@app.route('/financeiro')
def financeiro():
    return render_template('interno/financeiro.html')


@app.route('/financeiro/receita/nova', methods=['POST'])
def nova_receita():
    descricao = request.form.get('descricao', '')
    valor = request.form.get('valor', 0)
    data_emissao = request.form.get('data_emissao') or datetime.now().strftime('%Y-%m-%d')
    data_venc = request.form.get('data_venc') or data_emissao
    categoria = request.form.get('categoria', '')
    status = request.form.get('status', 'Aberto')
    id_cliente = request.form.get('id_cliente') or 0
    id_pedido = request.form.get('id_pedido') or 0

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO tb_contasReceber (id_cliente, id_pedido, descricao, valor, data_emissao, data_venc, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id_cliente, id_pedido, descricao, valor, data_emissao, data_venc, status))
        con.commit()
    except sqlite3.Error:
        con.rollback()
    finally:
        con.close()
    return redirect('/financeiro')


@app.route('/financeiro/despesa/nova', methods=['POST'])
def nova_despesa():
    descricao = request.form.get('descricao', '')
    valor = request.form.get('valor', 0)
    data_venc = request.form.get('data_venc') or datetime.now().strftime('%Y-%m-%d')
    categoria = request.form.get('categoria', '')
    status = request.form.get('status', 'Aberto')
    fornecedor = request.form.get('fornecedor', '')

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO tb_despesas (descricao, valor, data_venc, categoria, status, fornecedor)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (descricao, valor, data_venc, categoria, status, fornecedor))
        con.commit()
    except sqlite3.Error:
        con.rollback()
    finally:
        con.close()
    return redirect('/financeiro')


@app.route('/funcionarios.html')
@app.route('/funcionarios')
def funcionarios():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM tb_funcionarios')
        funcionarios = cur.fetchall()
    except sqlite3.Error:
        funcionarios = []
    finally:
        con.close()
    return render_template('interno/funcionarios.html', funcionarios=funcionarios)


@app.route('/novo-funcionario.html')
def view_novo_funcionario():
    return render_template('interno/novo-funcionario.html')


@app.route('/funcionario/novo', methods=['POST'])
def novo_funcionario_post():
    nome = request.form.get('nome', '')
    cpf = request.form.get('cpf', '')
    data_nasc = request.form.get('data_nasc', '')
    tel_cel = request.form.get('tel_cel', '')
    email_pessoal = request.form.get('email_pessoal', '')
    cargo = request.form.get('cargo', '')
    departamento = request.form.get('departamento', '')
    email_login = request.form.get('email_login', '')
    senha = request.form.get('senha', '')
    permissao = request.form.get('permissao', '')
    ativo = 1 if request.form.get('ativo') else 0

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO tb_funcionarios (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, ativo))
        con.commit()
    except sqlite3.Error:
        con.rollback()
    finally:
        con.close()
    return redirect('/funcionarios')


@app.route('/cliente.html')
@app.route('/cliente')
def clientes():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('SELECT * FROM tb_clientes')
        clientes = cur.fetchall()
    except sqlite3.Error:
        clientes = []
    finally:
        con.close()
    return render_template('interno/cliente.html', clientes=clientes)


@app.route('/pedido.html')
@app.route('/pedidos')
def pedidos():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute('''
            SELECT p.id_pedido, c.nome, p.data_pedido, p.valor_total, p.status, p.forma_pagamento, 1 as parcelas
            FROM tb_pedidos p
            LEFT JOIN tb_clientes c ON p.id_cliente = c.id_cliente
            ORDER BY p.data_pedido DESC
        ''')
        pedidos = cur.fetchall()
    except sqlite3.Error:
        pedidos = []
    finally:
        con.close()
    return render_template('interno/pedido.html', pedidos=pedidos)


@app.route('/configuracoes.html')
@app.route('/configuracoes')
def configuracoes():
    return render_template('interno/configuracoes.html')


@app.route('/login.html')
def login():
    return render_template('interno/login.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)