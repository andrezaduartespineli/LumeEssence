from flask import Flask, render_template, request, redirect, url_for, session, Response
import sqlite3
import os
from datetime import datetime
import csv
import io
import random
import math

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

# ==============================================================================
# DASHBOARD
# ==============================================================================
@app.route("/")
@app.route("/dashboard.html")
def dashboard():
    con = get_db()
    cur = con.cursor()
    
    # 1. KPI: Vendas Hoje
    cur.execute("SELECT SUM(valor_total) FROM tb_pedidos WHERE date(data_pedido) = date('now')")
    vendas_hoje = cur.fetchone()[0] or 0.0 

    # 2. KPI: Pedidos Pendentes
    cur.execute("SELECT COUNT(*) FROM tb_pedidos WHERE status = 'Pendente'")
    pedidos_pendentes = cur.fetchone()[0]

    # 3. KPI: Estoque Baixo
    cur.execute("SELECT COUNT(*) FROM tb_produtos WHERE qtd_estoque < 10")
    estoque_baixo = cur.fetchone()[0]

    # 4. KPI: Novos Clientes (Últimos 7 dias)
    cur.execute("SELECT COUNT(*) FROM tb_clientes WHERE date(data_cad) >= date('now', '-7 days')")
    novos_clientes = cur.fetchone()[0]

    # 5. Tabela de Últimos Pedidos
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
    return render_template("interno/dashboard.html", 
                           pedidos=ultimos_pedidos,
                           vendas_hoje=vendas_hoje,
                           pedidos_pendentes=pedidos_pendentes,
                           estoque_baixo=estoque_baixo,
                           novos_clientes=novos_clientes)

# ==============================================================================
# PRODUTOS
# ==============================================================================
@app.route("/produto.html")
@app.route("/produtos")
def listar_produtos():
    busca = request.args.get("q")
    filtro_cat = request.args.get("cat")
    
    con = get_db()
    cur = con.cursor()
    sql = "SELECT * FROM tb_produtos"
    condicoes = []
    parametros = []
    
    if busca:
        condicoes.append("(nome_produto LIKE ? OR sku LIKE ?)")
        parametros.append(f"%{busca}%"); parametros.append(f"%{busca}%")
        
    if filtro_cat and filtro_cat != 'Todos':
        condicoes.append("categoria = ?")
        parametros.append(filtro_cat)
    
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
        
    sql += " ORDER BY nome_produto ASC"

    try:
        cur.execute(sql, parametros)
        produtos = cur.fetchall()
    except:
        produtos = []
        
    con.close()
    return render_template("interno/produto.html", produtos=produtos, cat_atual=filtro_cat)

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
    categoria = request.form.get("categoria")
    aroma = request.form.get("aroma")
    variacao = request.form.get("variacao")
    ativo = request.form.get("ativo")
    data_cad = request.form.get("data_cad") or datetime.now().strftime("%Y-%m-%d")
    
    nome_imagem = "sem_foto.png"
    if 'img_produto' in request.files:
        file = request.files['img_produto']
        if file.filename != '':
            nome_imagem = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO tb_produtos (nome_produto, sku, descricao, preco_custo, preco_venda, 
            qtd_estoque, fornecedor, categoria, aroma, variacao, img_produto, data_cad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, sku, descricao, preco_custo, preco_venda, qtd_estoque, fornecedor, categoria, aroma, variacao, nome_imagem, data_cad))
        con.commit()
    except Exception as e:
        print(f"Erro ao salvar produto: {e}")
    con.close()
    return redirect("/produtos")

@app.route("/produto/delete/<int:id_produto>")
def deletar_produto(id_produto):
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM tb_produtos WHERE id_produto = ?", (id_produto,))
        con.commit()
    except Exception as e:
        print(f"Erro ao deletar: {e}")
    finally:
        con.close()
    return redirect("/produtos")

@app.route("/produto/editar/<int:id_produto>")
def editar_produto(id_produto):
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_produtos WHERE id_produto = ?", (id_produto,))
    produto = cur.fetchone()
    con.close()
    return render_template("interno/cad_produtos.html", produto=produto)

@app.route("/produto/atualizar", methods=["POST"])
def atualizar_produto():
    id_produto = request.form["id_produto"]
    nome = request.form.get("nome_produto")
    sku = request.form.get("sku")
    descricao = request.form.get("descricao")
    preco_custo = request.form.get("preco_custo")
    preco_venda = request.form.get("preco_venda")
    qtd_estoque = request.form.get("qtd_estoque")
    fornecedor = request.form.get("fornecedor")
    categoria = request.form.get("categoria")
    aroma = request.form.get("aroma")
    variacao = request.form.get("variacao")
    
    con = get_db()
    cur = con.cursor()
    
    if 'img_produto' in request.files and request.files['img_produto'].filename != '':
        file = request.files['img_produto']
        nome_imagem = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))
        cur.execute("""
            UPDATE tb_produtos SET 
            nome_produto=?, sku=?, descricao=?, preco_custo=?, preco_venda=?, 
            qtd_estoque=?, fornecedor=?, categoria=?, aroma=?, variacao=?, img_produto=?
            WHERE id_produto=?
        """, (nome, sku, descricao, preco_custo, preco_venda, qtd_estoque, fornecedor, categoria, aroma, variacao, nome_imagem, id_produto))
    else:
        cur.execute("""
            UPDATE tb_produtos SET 
            nome_produto=?, sku=?, descricao=?, preco_custo=?, preco_venda=?, 
            qtd_estoque=?, fornecedor=?, categoria=?, aroma=?, variacao=?
            WHERE id_produto=?
        """, (nome, sku, descricao, preco_custo, preco_venda, qtd_estoque, fornecedor, categoria, aroma, variacao, id_produto))

    con.commit()
    con.close()
    return redirect("/produtos")

# ==============================================================================
# FORNECEDORES
# ==============================================================================
@app.route("/fornecedores.html")
@app.route("/fornecedores")
def listar_fornecedores():
    busca = request.args.get("q")
    filtro_cat = request.args.get("categoria")
    con = get_db()
    cur = con.cursor()
    sql = "SELECT * FROM tb_fornecedores"
    condicoes = []
    parametros = []
    
    if busca:
        condicoes.append("(nome_fantasia LIKE ? OR razao_social LIKE ?)")
        parametros.append(f"%{busca}%"); parametros.append(f"%{busca}%")
    if filtro_cat and filtro_cat != 'Todos':
        condicoes.append("categoria = ?")
        parametros.append(filtro_cat)
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    sql += " ORDER BY nome_fantasia ASC"

    try:
        cur.execute(sql, parametros)
        dados = cur.fetchall()
    except:
        dados = []
    con.close()
    return render_template("interno/fornecedores.html", fornecedores=dados, cat_atual=filtro_cat)

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

@app.route("/fornecedor/delete/<int:id_fornecedor>")
def deletar_fornecedor(id_fornecedor):
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM tb_fornecedores WHERE id_fornecedor = ?", (id_fornecedor,))
        con.commit()
    except Exception as e:
        print(f"Erro ao deletar fornecedor: {e}")
    finally:
        con.close()
    return redirect("/fornecedores")

@app.route("/fornecedor/editar/<int:id_fornecedor>")
def editar_fornecedor(id_fornecedor):
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_fornecedores WHERE id_fornecedor = ?", (id_fornecedor,))
    fornecedor = cur.fetchone()
    con.close()
    return render_template("interno/novo-fornecedor.html", fornecedor=fornecedor)

@app.route("/fornecedor/atualizar", methods=["POST"])
def atualizar_fornecedor():
    id_fornecedor = request.form["id_fornecedor"]
    razao_social = request.form.get("razao_social")
    nome_fantasia = request.form.get("nome_fantasia")
    cnpj = request.form.get("cnpj")
    tel_cel = request.form.get("tel_cel")
    categoria = request.form.get("categoria")
    insc_estadual = request.form.get("insc_estadual")
    email = request.form.get("email")
    cep = request.form.get("cep")
    endereco = request.form.get("endereco")
    cidade = request.form.get("cidade")
    estado = request.form.get("estado")
    nome_repre = request.form.get("nome_repre")
    observacao = request.form.get("observacao")

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("""
            UPDATE tb_fornecedores SET 
            razao_social=?, nome_fantasia=?, cnpj=?, tel_cel=?, categoria=?, 
            insc_estadual=?, email=?, cep=?, endereco=?, cidade=?, estado=?, 
            nome_repre=?, observacao=?
            WHERE id_fornecedor=?
        """, (razao_social, nome_fantasia, cnpj, tel_cel, categoria, insc_estadual, email, cep, endereco, cidade, estado, nome_repre, observacao, id_fornecedor))
        con.commit()
    except Exception as e:
        print(f"Erro ao atualizar fornecedor: {e}")
    con.close()
    return redirect("/fornecedores")

# ==============================================================================
# FINANCEIRO
# ==============================================================================
@app.route("/financeiro.html")
@app.route("/financeiro")
def financeiro():
    filtro = request.args.get("filtro", "atual")
    con = get_db()
    cur = con.cursor()
    where_clause = ""
    if filtro == 'atual':
        where_clause = "WHERE strftime('%Y-%m', data_venc) = strftime('%Y-%m', 'now')"
    elif filtro == 'anterior':
        where_clause = "WHERE strftime('%Y-%m', data_venc) = strftime('%Y-%m', 'now', '-1 month')"
    
    cur.execute(f"SELECT * FROM tb_contasReceber {where_clause}")
    receitas_db = cur.fetchall()
    cur.execute(f"SELECT * FROM tb_despesas {where_clause}")
    despesas_db = cur.fetchall()
    con.close()

    extrato = []
    total_receitas = 0
    total_despesas = 0

    for r in receitas_db:
        valor = float(r['valor'])
        total_receitas += valor
        extrato.append({'data': r['data_venc'], 'descricao': r['descricao'], 'categoria': r['categoria'], 'status': r['status'], 'valor': valor, 'tipo': 'entrada'})

    for d in despesas_db:
        valor = float(d['valor'])
        total_despesas += valor
        extrato.append({'data': d['data_venc'], 'descricao': d['descricao'], 'categoria': d['categoria'], 'status': d['status'], 'valor': valor, 'tipo': 'saida'})

    extrato.sort(key=lambda x: x['data'], reverse=True)
    saldo_liquido = total_receitas - total_despesas
    return render_template("interno/financeiro.html", extrato=extrato, total_receitas=total_receitas, total_despesas=total_despesas, saldo=saldo_liquido, filtro_atual=filtro)

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
    cur.execute("INSERT INTO tb_contasReceber (descricao, valor, data_emissao, data_venc, categoria, status) VALUES (?, ?, ?, ?, ?, ?)", (descricao, valor, data_emissao, data_venc, categoria, status))
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
    cur.execute("INSERT INTO tb_despesas (descricao, valor, data_venc, categoria, status, fornecedor) VALUES (?, ?, ?, ?, ?, ?)", (descricao, valor, data_venc, categoria, status, fornecedor))
    con.commit()
    con.close()
    return redirect("/financeiro")

# ==============================================================================
# FUNCIONÁRIOS
# ==============================================================================
@app.route("/funcionarios.html")
@app.route("/funcionarios")
def funcionarios():
    busca = request.args.get("q")
    con = get_db()
    cur = con.cursor()
    sql = "SELECT * FROM tb_funcionarios"
    if busca:
        sql += f" WHERE nome LIKE '%{busca}%' OR cargo LIKE '%{busca}%'"
    sql += " ORDER BY nome ASC"
    try:
        cur.execute(sql)
        dados = cur.fetchall()
    except:
        dados = []
    con.close()
    return render_template("interno/funcionarios.html", funcionarios=dados)

@app.route("/novo-funcionario.html")
@app.route("/funcionario/editar/<int:id_funcionario>")
def view_funcionario_form(id_funcionario=None):
    funcionario = None
    if id_funcionario:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM tb_funcionarios WHERE id_funcionario = ?", (id_funcionario,))
        funcionario = cur.fetchone()
        con.close()
    return render_template("interno/novo-funcionario.html", funcionario=funcionario)

@app.route("/funcionario/salvar", methods=["POST"])
def salvar_funcionario():
    id_funcionario = request.form.get("id_funcionario")
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
    
    con = get_db()
    cur = con.cursor()
    nome_imagem = None
    if 'img_funcionario' in request.files:
        file = request.files['img_funcionario']
        if file.filename != '':
            nome_imagem = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))

    try:
        if id_funcionario:
            sql = "UPDATE tb_funcionarios SET nome=?, cpf=?, data_nasc=?, tel_cel=?, email_pessoal=?, cargo=?, departamento=?, email_login=?, permissao=?"
            params = [nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, permissao]
            if senha:
                sql += ", senha=?"
                params.append(senha)
            if nome_imagem:
                sql += ", img_funcionario=?"
                params.append(nome_imagem)
            sql += " WHERE id_funcionario=?"
            params.append(id_funcionario)
            cur.execute(sql, params)
        else:
            if not nome_imagem: nome_imagem = "sem_foto_user.png" 
            cur.execute("""
                INSERT INTO tb_funcionarios (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, 
                departamento, email_login, senha, permissao, img_funcionario, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, nome_imagem))
        con.commit()
    except Exception as e:
        print(f"Erro ao salvar funcionário: {e}")
    finally:
        con.close()
    return redirect("/funcionarios")

@app.route("/funcionario/delete/<int:id_funcionario>")
def deletar_funcionario(id_funcionario):
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM tb_funcionarios WHERE id_funcionario = ?", (id_funcionario,))
        con.commit()
    except: pass
    con.close()
    return redirect("/funcionarios")

@app.route("/funcionario/status/<int:id_funcionario>/<int:novo_status>")
def status_funcionario(id_funcionario, novo_status):
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("UPDATE tb_funcionarios SET ativo = ? WHERE id_funcionario = ?", (novo_status, id_funcionario))
        con.commit()
    except: pass
    con.close()
    return redirect("/funcionarios")

# ==============================================================================
# CLIENTES (COM PAGINAÇÃO - SEM LOGIN)
# ==============================================================================
@app.route("/cliente.html")
@app.route("/cliente")
def clientes():
    POR_PAGINA = 10
    pagina_atual = request.args.get('page', 1, type=int)
    busca = request.args.get("q", "")
    
    con = get_db()
    cur = con.cursor()
    
    if busca:
        condicao_where = "WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ?"
        termo = f"%{busca}%"
        params = [termo, termo, termo]
    else:
        condicao_where = ""
        params = []

    cur.execute(f"SELECT COUNT(*) FROM tb_clientes {condicao_where}", params)
    total_registros = cur.fetchone()[0]
    total_paginas = math.ceil(total_registros / POR_PAGINA)
    
    offset = (pagina_atual - 1) * POR_PAGINA
    params_final = params + [POR_PAGINA, offset]
    
    cur.execute(f"""
        SELECT * FROM tb_clientes 
        {condicao_where}
        ORDER BY id_cliente DESC LIMIT ? OFFSET ?
    """, params_final)
    
    clientes_encontrados = cur.fetchall()
    con.close()
    
    return render_template("interno/cliente.html", clientes=clientes_encontrados, pagina_atual=pagina_atual, total_paginas=total_paginas, termo_busca=busca, total_registros=total_registros)

@app.route("/admin/cliente/excluir/<int:id_cliente>")
def admin_excluir_cliente(id_cliente):
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM tb_enderecos WHERE id_cliente = ?", (id_cliente,))
        cur.execute("DELETE FROM tb_cartoes WHERE id_cliente = ?", (id_cliente,))
        cur.execute("DELETE FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
        con.commit()
    except: pass
    con.close()
    return redirect("/cliente.html")

@app.route("/admin/cliente/editar", methods=['POST'])
def admin_editar_cliente():
    try:
        id_cliente = request.form['id_cliente']
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        tel_cel = request.form['whatsapp']
        con = get_db()
        cur = con.cursor()
        cur.execute("UPDATE tb_clientes SET nome = ?, email = ?, cpf = ?, tel_cel = ? WHERE id_cliente = ?", (nome, email, cpf, tel_cel, id_cliente))
        con.commit()
        con.close()
    except: pass
    return redirect("/cliente.html")

# ==============================================================================
# OUTROS
# ==============================================================================
@app.route("/mensagens.html")
@app.route("/mensagens")
def mensagens():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM tb_contatos ORDER BY data_contato DESC")
        msgs = cur.fetchall()
    except: msgs = []
    con.close()
    return render_template("interno/mensagens.html", mensagens=msgs)

@app.route("/newsletter.html")
@app.route("/newsletter")
def newsletter():
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM tb_newsletter ORDER BY data_cad DESC")
        leads = cur.fetchall()
    except: leads = []
    con.close()
    return render_template("interno/newsletter.html", leads=leads)

@app.route("/configuracoes.html")
@app.route("/configuracoes")
def configuracoes():
    return render_template("interno/configuracoes.html")

# ==============================================================================
# PEDIDOS (COM PAGINAÇÃO - SEM LOGIN)
# ==============================================================================
@app.route("/pedido.html")
@app.route("/pedidos")
def pedidos():
    POR_PAGINA = 10
    pagina_atual = request.args.get('page', 1, type=int)
    busca = request.args.get("q")
    filtro_status = request.args.get("status")
    
    con = get_db()
    cur = con.cursor()
    
    sql_base = "FROM tb_pedidos p JOIN tb_clientes c ON p.id_cliente = c.id_cliente"
    condicoes = []
    parametros = []
    if busca:
        condicoes.append("(p.id_pedido LIKE ? OR c.nome LIKE ?)")
        parametros.append(f"%{busca}%"); parametros.append(f"%{busca}%")
    if filtro_status and filtro_status != 'Todos':
        condicoes.append("p.status = ?")
        parametros.append(filtro_status)
    
    clausula_where = ""
    if condicoes:
        clausula_where = " WHERE " + " AND ".join(condicoes)

    cur.execute(f"SELECT COUNT(*) {sql_base} {clausula_where}", parametros)
    total_registros = cur.fetchone()[0]
    total_paginas = math.ceil(total_registros / POR_PAGINA)
    offset = (pagina_atual - 1) * POR_PAGINA
    
    sql_final = f"""
        SELECT p.id_pedido, c.nome, p.data_pedido, p.valor_total, p.status, p.forma_pagamento, p.parcelas
        {sql_base} {clausula_where} ORDER BY p.data_pedido DESC LIMIT ? OFFSET ?
    """
    parametros_finais = parametros + [POR_PAGINA, offset]
    try:
        cur.execute(sql_final, parametros_finais)
        lista_pedidos = cur.fetchall()
    except: lista_pedidos = []
    con.close()
    
    return render_template("interno/pedido.html", pedidos=lista_pedidos, status_atual=filtro_status, pagina_atual=pagina_atual, total_paginas=total_paginas, total_registros=total_registros, termo_busca=busca)

# ==============================================================================
# LOGIN (MANTIDO, MAS SEM BLOQUEAR AS OUTRAS PÁGINAS)
# ==============================================================================
@app.route("/login.html")
def view_login():
    if 'id_usuario' in session: return redirect("/dashboard.html")
    return render_template("interno/login.html")

@app.route("/login", methods=['POST'])
def fazer_login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_funcionarios WHERE email_login = ? AND senha = ? AND ativo = 1", (email, senha))
    usuario = cur.fetchone()
    con.close()
    if usuario:
        session['id_usuario'] = usuario['id_funcionario']
        session['nome_usuario'] = usuario['nome']
        session['cargo'] = usuario['cargo']
        return redirect("/dashboard.html")
    else:
        return render_template("interno/login.html", erro="Dados incorretos.")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login.html")

# ==============================================================================
# CSV
# ==============================================================================
@app.route("/gerar_planilha_padrao")
def gerar_planilha_padrao():
    categorias = {
        "Velas Aromáticas": {"prefixo": "VEL", "custo": 25.00, "venda": 59.90, "var": "150g"},
        "Home Spray":       {"prefixo": "HOM", "custo": 18.00, "venda": 45.00, "var": "250ml"},
        "Difusores":        {"prefixo": "DIF", "custo": 30.00, "venda": 75.00, "var": "200ml"},
        "Kits Presente":    {"prefixo": "KIT", "custo": 55.00, "venda": 129.90, "var": "Kit M"}
    }
    aromas = ["Lavanda", "Alecrim", "Bamboo", "Baunilha", "Limão Siciliano", "Jasmim", "Coco", "Morango", "Flor de Algodão", "Capim Limão"]
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["nome_produto", "sku", "descricao", "preco_custo", "preco_venda", "qtd_estoque", "fornecedor", "categoria", "aroma", "variacao"])
    
    for cat_nome, cat_dados in categorias.items():
        aromas_selecionados = random.sample(aromas, 5)
        for i, aroma in enumerate(aromas_selecionados, 1):
            sku = f"{cat_dados['prefixo']}-{str(i).zfill(3)}"
            nome = f"{cat_nome[:-1]} {aroma}" if cat_nome.endswith('s') else f"{cat_nome} {aroma}"
            descricao = f"Produto artesanal da linha {cat_nome} com essência premium de {aroma}."
            writer.writerow([nome, sku, descricao, str(cat_dados['custo']).replace('.', ','), str(cat_dados['venda']).replace('.', ','), random.randint(10, 50), "Produção Própria", cat_nome, aroma, cat_dados['var']])
    
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=novos_produtos.csv"})

@app.route("/importar_csv", methods=["POST"])
def importar_csv():
    if 'arquivo_csv' not in request.files: return "Nenhum arquivo enviado", 400
    file = request.files['arquivo_csv']
    if file.filename == '': return "Nenhum arquivo selecionado", 400

    if file:
        stream = io.TextIOWrapper(file.stream._file, "utf-8", newline='')
        csv_input = csv.DictReader(stream, delimiter=';')
        con = get_db()
        cur = con.cursor()
        try:
            for row in csv_input:
                img_padrao = "sem_foto.png"
                ativo = 1
                data_hoje = datetime.now().strftime("%Y-%m-%d")
                preco_custo = row['preco_custo'].replace(',', '.')
                preco_venda = row['preco_venda'].replace(',', '.')
                cur.execute("""
                    INSERT INTO tb_produtos (nome_produto, sku, descricao, preco_custo, preco_venda,
                    qtd_estoque, fornecedor, categoria, aroma, variacao, img_produto, ativo, data_cad) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (row['nome_produto'], row['sku'], row['descricao'], preco_custo, preco_venda, row['qtd_estoque'], row['fornecedor'], row['categoria'], row['aroma'], row['variacao'], img_padrao, ativo, data_hoje))
            con.commit()
        except Exception as e:
            con.rollback()
            return f"Erro na importação: {str(e)}", 500
        finally:
            con.close()
        return redirect("/cad_produtos.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)