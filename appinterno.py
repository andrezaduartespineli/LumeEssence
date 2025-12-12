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
    
    # 1. KPI: Vendas Hoje (Soma)
    # A função date('now') compara apenas a parte do dia, ignorando as horas
    cur.execute("SELECT SUM(valor_total) FROM tb_pedidos WHERE date(data_pedido) = date('now')")
    vendas_hoje = cur.fetchone()[0]
    # Se não tiver vendas, o banco retorna None, então transformamos em 0.0
    vendas_hoje = vendas_hoje if vendas_hoje else 0.0 

    # 2. KPI: Pedidos Pendentes (Contagem)
    cur.execute("SELECT COUNT(*) FROM tb_pedidos WHERE status = 'Pendente'")
    pedidos_pendentes = cur.fetchone()[0]

    # 3. KPI: Estoque Baixo (Contagem de produtos com menos de 10 itens)
    cur.execute("SELECT COUNT(*) FROM tb_produtos WHERE qtd_estoque < 10")
    estoque_baixo = cur.fetchone()[0]

    # 4. KPI: Novos Clientes (Últimos 7 dias)
    # Conta registros onde a data é maior ou igual a "hoje menos 7 dias"
    cur.execute("SELECT COUNT(*) FROM tb_clientes WHERE date(data_cad) >= date('now', '-7 days')")
    novos_clientes = cur.fetchone()[0]

    # 5. Tabela de Últimos Pedidos (Já tínhamos feito, mantemos aqui)
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
    
    # Enviamos todas essas variáveis novas para o template
    return render_template("interno/dashboard.html", 
                           pedidos=ultimos_pedidos,
                           vendas_hoje=vendas_hoje,
                           pedidos_pendentes=pedidos_pendentes,
                           estoque_baixo=estoque_baixo,
                           novos_clientes=novos_clientes)

# --- Produtos ---
@app.route("/produto.html")
@app.route("/produtos")
def listar_produtos():
    # 1. Captura os parâmetros
    busca = request.args.get("q")
    filtro_cat = request.args.get("cat") # Vai receber o ID (1, 2, 3...)
    
    con = get_db()
    cur = con.cursor()
    
    # 2. SQL Base
    sql = "SELECT * FROM tb_produtos"
    
    condicoes = []
    parametros = []
    
    # 3. Lógica dos Filtros
    
    # Busca por texto (Nome ou SKU)
    if busca:
        condicoes.append("(nome_produto LIKE ? OR sku LIKE ?)")
        parametros.append(f"%{busca}%")
        parametros.append(f"%{busca}%")
        
    # Filtro por Categoria (Se foi clicado um botão)
    if filtro_cat and filtro_cat != 'Todos':
        condicoes.append("categoria_id = ?")
        parametros.append(filtro_cat)
    
    # 4. Monta o SQL Final
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
        
    # Ordena por nome
    sql += " ORDER BY nome_produto ASC"

    try:
        cur.execute(sql, parametros)
        produtos = cur.fetchall()
    except:
        produtos = []
        
    con.close()
    
    # Envia 'cat_atual' para o HTML pintar o botão certo
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

# --- Rota para DELETAR Produto ---
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

# --- Rota para ABRIR O FORMULÁRIO de Edição ---
@app.route("/produto/editar/<int:id_produto>")
def editar_produto(id_produto):
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_produtos WHERE id_produto = ?", (id_produto,))
    produto = cur.fetchone()
    con.close()
    
    # Reutilizamos a mesma tela de cadastro, mas passando os dados do produto
    return render_template("interno/cad_produtos.html", produto=produto)

# --- Rota para SALVAR A EDIÇÃO (Update) ---
@app.route("/produto/atualizar", methods=["POST"])
def atualizar_produto():
    id_produto = request.form["id_produto"]
    
    # Captura os dados do formulário
    nome = request.form.get("nome_produto")
    sku = request.form.get("sku")
    descricao = request.form.get("descricao")
    preco_custo = request.form.get("preco_custo")
    preco_venda = request.form.get("preco_venda")
    qtd_estoque = request.form.get("qtd_estoque")
    fornecedor = request.form.get("fornecedor")
    categoria = request.form.get("categoria") # Se estiver usando texto direto
    # Se estiver usando IDs de categoria, ajuste conforme seu banco
    
    con = get_db()
    cur = con.cursor()
    
    # Lógica da Imagem: Só atualiza se o usuário enviou uma nova
    if 'img_produto' in request.files and request.files['img_produto'].filename != '':
        file = request.files['img_produto']
        nome_imagem = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))
        
        # Atualiza COM imagem
        cur.execute("""
            UPDATE tb_produtos SET 
            nome_produto=?, sku=?, descricao=?, preco_custo=?, preco_venda=?, 
            qtd_estoque=?, fornecedor=?, categoria=?, img_produto=?
            WHERE id_produto=?
        """, (nome, sku, descricao, preco_custo, preco_venda, qtd_estoque, fornecedor, categoria, nome_imagem, id_produto))
    else:
        # Atualiza SEM mudar a imagem antiga
        cur.execute("""
            UPDATE tb_produtos SET 
            nome_produto=?, sku=?, descricao=?, preco_custo=?, preco_venda=?, 
            qtd_estoque=?, fornecedor=?, categoria=?
            WHERE id_produto=?
        """, (nome, sku, descricao, preco_custo, preco_venda, qtd_estoque, fornecedor, categoria, id_produto))

    con.commit()
    con.close()
    return redirect("/produtos")

# --- Fornecedores ---
@app.route("/fornecedores.html")
@app.route("/fornecedores")
def listar_fornecedores():
    # 1. Captura os parâmetros
    busca = request.args.get("q")
    filtro_cat = request.args.get("categoria")
    
    con = get_db()
    cur = con.cursor()
    
    # 2. SQL Base
    sql = "SELECT * FROM tb_fornecedores"
    
    condicoes = []
    parametros = []
    
    # 3. Lógica dos Filtros
    
    # Se tiver busca digitada (Nome Fantasia ou Razão Social)
    if busca:
        condicoes.append("(nome_fantasia LIKE ? OR razao_social LIKE ?)")
        parametros.append(f"%{busca}%")
        parametros.append(f"%{busca}%")
        
    # Se tiver filtro de categoria clicado (e não for 'Todos')
    if filtro_cat and filtro_cat != 'Todos':
        condicoes.append("categoria = ?")
        parametros.append(filtro_cat)
    
    # 4. Monta o SQL Final
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
        
    # Ordena alfabeticamente
    sql += " ORDER BY nome_fantasia ASC"

    try:
        cur.execute(sql, parametros)
        dados = cur.fetchall()
    except:
        dados = []
        
    con.close()
    
    # Envia 'cat_atual' para o HTML pintar o botão certo
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

# --- Financeiro ---
@app.route("/financeiro.html")
@app.route("/financeiro")
def financeiro():
    # 1. Pega o filtro da URL (Padrão: 'atual' = Este Mês)
    filtro = request.args.get("filtro", "atual")
    
    con = get_db()
    cur = con.cursor()
    
    # 2. Define a Cláusula WHERE baseada na escolha
    where_clause = ""
    
    if filtro == 'atual':
        # Pega registros onde Ano-Mês é igual ao Ano-Mês de hoje ('now')
        where_clause = "WHERE strftime('%Y-%m', data_venc) = strftime('%Y-%m', 'now')"
        
    elif filtro == 'anterior':
        # Pega registros onde Ano-Mês é igual ao Mês Passado
        where_clause = "WHERE strftime('%Y-%m', data_venc) = strftime('%Y-%m', 'now', '-1 month')"
        
    # Se filtro for 'todos', o where_clause fica vazio ("") e busca tudo
    
    # 3. Buscar Receitas com Filtro
    cur.execute(f"SELECT * FROM tb_contasReceber {where_clause}")
    receitas_db = cur.fetchall()
    
    # 4. Buscar Despesas com Filtro
    cur.execute(f"SELECT * FROM tb_despesas {where_clause}")
    despesas_db = cur.fetchall()
    
    con.close()

    # 5. Processamento (Igual ao anterior)
    extrato = []
    total_receitas = 0
    total_despesas = 0

    for r in receitas_db:
        valor = float(r['valor'])
        total_receitas += valor
        extrato.append({
            'data': r['data_venc'],
            'descricao': r['descricao'],
            'categoria': r['categoria'],
            'status': r['status'],
            'valor': valor,
            'tipo': 'entrada'
        })

    for d in despesas_db:
        valor = float(d['valor'])
        total_despesas += valor
        extrato.append({
            'data': d['data_venc'],
            'descricao': d['descricao'],
            'categoria': d['categoria'],
            'status': d['status'],
            'valor': valor,
            'tipo': 'saida'
        })

    extrato.sort(key=lambda x: x['data'], reverse=True)
    saldo_liquido = total_receitas - total_despesas

    # Enviamos 'filtro_atual' para o HTML saber qual botão pintar
    return render_template("interno/financeiro.html", 
                           extrato=extrato, 
                           total_receitas=total_receitas, 
                           total_despesas=total_despesas, 
                           saldo=saldo_liquido,
                           filtro_atual=filtro)
    
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
    busca = request.args.get("q")
    con = get_db()
    cur = con.cursor()
    
    if busca:
        termo = f"%{busca}%"
        cur.execute("""
            SELECT * FROM tb_funcionarios 
            WHERE nome LIKE ? OR cargo LIKE ? OR departamento LIKE ?
        """, (termo, termo, termo))
    else:
        cur.execute("SELECT * FROM tb_funcionarios")
        
    dados = cur.fetchall()
    con.close()
    return render_template("interno/funcionarios.html", funcionarios=dados)


@app.route("/novo-funcionario.html")
def view_novo_funcionario():
    return render_template("interno/novo-funcionario.html")

@app.route("/funcionario/novo", methods=["POST"])
def novo_funcionario_post():
    print("--- Tentando cadastrar funcionário ---")
    
    # Dados de texto
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

    # Lógica de Upload da Foto
    nome_arquivo = "sem_foto_humano.png" # Foto padrão se não enviar nada
    if 'foto' in request.files:
        arquivo = request.files['foto']
        if arquivo.filename != "":
            # Cria um nome seguro e único para não substituir fotos de outros
            import os
            from werkzeug.utils import secure_filename
            
            nome_seguro = secure_filename(arquivo.filename)
            # Salva na pasta uploads
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro))
            nome_arquivo = nome_seguro

    con = get_db()
    cur = con.cursor()
    
    try:
        # Note que adicionei a coluna 'foto' no INSERT
        cur.execute("""
            INSERT INTO tb_funcionarios (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, foto, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, nome_arquivo, ativo))
        
        con.commit()
        return redirect("/funcionarios")
        
    except Exception as e:
        con.rollback()
        print(f"❌ ERRO: {e}")
        return f"Erro ao salvar: {e}"
    finally:
        con.close()

# --- Clientes ---
@app.route("/cliente.html")
@app.route("/cliente")
def clientes():
    busca = request.args.get("q") # Pega o que foi digitado
    
    con = get_db()
    cur = con.cursor()

    if busca:
        # O símbolo % serve para buscar em qualquer parte do texto (começo, meio ou fim)
        termo = f"%{busca}%"
        cur.execute("""
            SELECT * FROM tb_clientes 
            WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ?
        """, (termo, termo, termo))
    else:
        # Se não digitou nada, traz tudo
        cur.execute("SELECT * FROM tb_clientes")

    clientes = cur.fetchall()
    con.close()
    
    return render_template("interno/cliente.html", clientes=clientes)

# --- Mensagens de Contato (Fale Conosco) ---
@app.route("/mensagens.html")
@app.route("/mensagens")
def mensagens():
    con = get_db()
    cur = con.cursor()
    # Busca as mensagens, da mais recente para a mais antiga
    try:
        cur.execute("SELECT * FROM tb_contatos ORDER BY data_contato DESC")
        msgs = cur.fetchall()
    except:
        msgs = []
    con.close()
    return render_template("interno/mensagens.html", mensagens=msgs)

# --- Newsletter (Leads) ---
@app.route("/newsletter.html")
@app.route("/newsletter")
def newsletter():
    con = get_db()
    cur = con.cursor()
    # Busca os leads do mais recente para o mais antigo
    try:
        cur.execute("SELECT * FROM tb_newsletter ORDER BY data_cad DESC")
        leads = cur.fetchall()
    except:
        leads = []
    con.close()
    return render_template("interno/newsletter.html", leads=leads)

# --- Pedidos (Visualização Admin) ---
@app.route("/pedido.html")
@app.route("/pedidos")
def pedidos():
    # 1. Captura os parâmetros da URL
    busca = request.args.get("q")
    filtro_status = request.args.get("status")
    
    con = get_db()
    cur = con.cursor()
    
    # 2. Query Base
    sql = """
        SELECT p.id_pedido, c.nome, p.data_pedido, p.valor_total, p.status, p.forma_pagamento, p.parcelas
        FROM tb_pedidos p
        JOIN tb_clientes c ON p.id_cliente = c.id_cliente
    """
    
    condicoes = []
    parametros = []

    # 3. Lógica de Filtros Dinâmicos
    
    # Se tiver busca por texto (Nome ou ID)
    if busca:
        condicoes.append("(p.id_pedido LIKE ? OR c.nome LIKE ?)")
        parametros.append(f"%{busca}%")
        parametros.append(f"%{busca}%")
    
    # Se tiver filtro por botão de status (Ignora se for 'Todos')
    if filtro_status and filtro_status != 'Todos':
        condicoes.append("p.status = ?")
        parametros.append(filtro_status)

    # 4. Monta o SQL Final
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    
    sql += " ORDER BY p.data_pedido DESC"

    try:
        cur.execute(sql, parametros)
        pedidos = cur.fetchall()
    except Exception as e:
        print(f"Erro no filtro: {e}")
        pedidos = []
        
    con.close()
    
    # Envia 'status_atual' para o HTML saber qual botão pintar de ativo
    return render_template("interno/pedido.html", pedidos=pedidos, status_atual=filtro_status)



@app.route("/configuracoes.html")
@app.route("/configuracoes")
def configuracoes():
    return render_template("interno/configuracoes.html")

@app.route("/login.html")
def login():
    return render_template("interno/login.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)