from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import json
import uuid
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_lume_essence'  # Necessário para sessões (login)

# --- Conexão com Banco ---
def get_db():
    conn = sqlite3.connect("db_lume.db")
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

# --- Rotas Públicas ---
@app.route("/")
@app.route("/index.html")
def index():
    return render_template("site/index.html")

@app.route("/produtos")
@app.route("/produtos.html")
def produtos():
    con = get_db()
    cur = con.cursor()
    
    # Busca apenas produtos que estão marcados como ATIVOS no cadastro (opcional)
    # Se não tiver coluna 'ativo', use: SELECT * FROM tb_produtos
    cur.execute("SELECT * FROM tb_produtos") 
    
    lista_produtos = cur.fetchall()
    con.close()
    
    return render_template("site/produtos.html", produtos=lista_produtos)

@app.route("/sobre")
@app.route("/sobre.html")
def sobre():
    return render_template("site/sobre.html")

@app.route("/contato")
@app.route("/contato.html")
def contato():
    return render_template("site/contato.html")


@app.route("/cadastro.html")
@app.route("/cadastro")
def cadastro_page():
    return render_template("site/cadastro.html")

@app.route("/contato/enviar", methods=["POST"])
def enviar_contato():
    nome = request.form["nome"]
    email = request.form["email"]
    tel_cel = request.form["tel_cel"]
    mensagem = request.form["mensagem"]
    data_contato = datetime.now()

    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO tb_contatos (nome, email, tel_cel, mensagem, data_contato) VALUES (?, ?, ?, ?, ?)",
                (nome, email, tel_cel, mensagem, data_contato))
    con.commit()
    con.close()
    return redirect("/contato")

# --- Newsletter ---
@app.route("/newsletter/cadastrar", methods=["POST"])
def cadastrar_newsletter():
    nome = request.form["nome"]
    whatsapp = request.form["whatsapp"]
    email = request.form["email"]
    data_cad = datetime.now()

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO tb_newsletter (nome, whatsapp, email, data_cad) VALUES (?, ?, ?, ?)",
                    (nome, whatsapp, email, data_cad))
        con.commit()
    except:
        pass # Ignora erro se já existir
    con.close()
    return redirect("/")

# --- Autenticação (Login/Cadastro) ---
@app.route ("/login")
@app.route ("/login.html")
def login_page():
    return render_template("site/login.html")

# Rotas compatíveis com links relativos que apontam para /site/login.html
@app.route("/site/login.html")
@app.route("/site/login")
def site_login_alias():
    return render_template("site/login.html")

# Alias para /site/cadastro.html (links relativos dentro de /site/* esperam esse caminho)
@app.route("/site/cadastro.html")
@app.route("/site/cadastro")
def site_cadastro_alias():
    return render_template("site/cadastro.html")

@app.route("/verificar_email", methods=["POST"])
def verificar_email():
    dados = request.get_json()
    email = dados.get("email")
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT id_cliente FROM tb_clientes WHERE email = ?", (email,))
    user = cur.fetchone()
    con.close()
    return jsonify({"existe": bool(user)})

@app.route("/cadastro-cliente", methods=["POST"])
def cadastro_cliente():
    # Recebe todos os campos do seu HTML
    nome = request.form["nome"]
    data_nasc = request.form["data_nasc"]
    cpf = request.form["cpf"]
    genero = request.form["genero"]
    tel_cel = request.form["tel_cel"]
    email = request.form["email"]
    cep = request.form["cep"]
    endereco = request.form["endereco"]
    n = request.form["n"]
    complemento = request.form.get("complemento", "")
    referencia = request.form.get("referencia", "")
    bairro = request.form["bairro"]
    cidade = request.form["cidade"]
    estado = request.form["estado"]
    senha = request.form["senha"] # Ideal: usar hash
    data_cad = datetime.now()

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO tb_clientes (nome, data_nasc, cpf, genero, tel_cel, email, cep, endereco, n, complemento, referencia, bairro, cidade, estado, senha, data_cad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, data_nasc, cpf, genero, tel_cel, email, cep, endereco, n, complemento, referencia, bairro, cidade, estado, senha, data_cad))
    con.commit()
    
    # Loga o usuário automaticamente
    session['user_id'] = cur.lastrowid
    session['user_nome'] = nome
    con.close()
    
    return redirect("/area_cliente/area-cliente.html") # Ajuste a rota conforme necessário

# --- Carrinho e Checkout ---
@app.route("/carrinho")
def carrinho():
    return render_template("site/carrinho.html")

@app.route("/carrinho.html")
def carrinho_html():
    return render_template("site/carrinho.html")

# Alias para links relativos que apontam para /site/carrinho.html (ex.: ../site/carrinho.html)
@app.route("/site/carrinho.html")
@app.route("/site/carrinho")
def site_carrinho_alias():
    return render_template("site/carrinho.html")

@app.route("/checkout")
def checkout():
    # Verifica se está logado (Simples)
    # if 'user_id' not in session:
    #     return redirect("/login")
    return render_template("site/checkout.html")

@app.route("/checkout.html")
def checkout_html():
    return render_template("site/checkout.html")

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    # 1. Dados Gerais
    id_cliente = request.form.get("id_cliente", 1) # Padrão 1 se não estiver logado (teste)
    if 'user_id' in session:
        id_cliente = session['user_id']
        
    valor_total = request.form["total_pedido"]
    forma_pagamento = request.form["forma_pagamento"]
    lista_itens_json = request.form["lista_itens"]
    try:
        qtd_parcelas = int(request.form.get("parcelas_escolhidas", 1))
    except Exception:
        qtd_parcelas = 1
    
    con = get_db()
    cur = con.cursor()

    try:
        # --- Lógica do Cartão (Simulação) ---
        if forma_pagamento == 'credit':
            card_number = request.form.get("card_number_sent", "")
            save_option = request.form.get("save_card_option", "nao")

            if save_option == 'sim' and card_number:
                nome_titular = request.form.get("card_holder_sent")
                validade = request.form.get("card_expiry_sent")
                ultimos_4 = card_number.replace(" ", "")[-4:]
                bandeira = "Visa" if card_number.startswith("4") else "Mastercard"
                token_falso = str(uuid.uuid4())

                # tb_cartoes tem coluna 'parcelas' no schema; gravamos também aí
                cur.execute("""
                    INSERT INTO tb_cartoes (id_cliente, nome_titular, ultimos_4, bandeira, token_pagamento, validade, parcelas)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (id_cliente, nome_titular, ultimos_4, bandeira, token_falso, validade, qtd_parcelas))

        # 2. Salvar Pedido
        data_atual = datetime.now()
        data_entrega = datetime.now() # Adicione dias se quiser

        # Inserir pedido (schema tb_pedidos não tem coluna 'parcelas')
        cur.execute("""
            INSERT INTO tb_pedidos (id_cliente, data_pedido, status, valor_total, data_entrega, forma_pagamento)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_cliente, data_atual, 'Pendente', valor_total, data_entrega, forma_pagamento))
        
        id_novo_pedido = cur.lastrowid 

        # 3. Salvar Itens
        itens = json.loads(lista_itens_json)
        for item in itens:
            subtotal = float(item['qtd']) * float(item['preco'])
            cur.execute("""
                INSERT INTO tb_itensPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (id_novo_pedido, item['id_produto'], item['qtd'], item['preco'], subtotal))

        con.commit()
        return redirect("/area_cliente/meus-pedidos") # Sucesso

    except Exception as e:
        con.rollback()
        print(f"Erro: {e}")
        return f"Erro ao processar pedido: {e}"
    finally:
        con.close()

# --- Área do Cliente (Rotas de Visualização) ---
@app.route("/area_cliente/area-cliente.html") # Mantendo o nome do arquivo para facilitar
def area_cliente_home():
    return render_template("area_cliente/area-cliente.html")

@app.route("/area_cliente/meus-pedidos.html")
def area_cliente_pedidos():
    # 1. Verifica se está logado
    if 'user_id' not in session:
        return redirect("/login")
    
    id_cliente_logado = session['user_id']

    con = get_db()
    cur = con.cursor()
    
    # 2. Busca APENAS os pedidos desse cliente (WHERE id_cliente = ?)
    # Também fazemos JOIN com 'tb_itensPedido' e 'tb_produtos' se quisermos mostrar os itens,
    # mas para simplificar a lista principal, vamos pegar só os dados do pedido.
    cur.execute("""
        SELECT * FROM tb_pedidos 
        WHERE id_cliente = ? 
        ORDER BY data_pedido DESC
    """, (id_cliente_logado,))
    
    meus_pedidos = cur.fetchall()
    con.close()

    return render_template("area_cliente/meus-pedidos.html", pedidos=meus_pedidos)


# Demais rotas da área do cliente (favoritos, endereços, etc)...
@app.route("/area_cliente/<page>")
def area_cliente_pages(page):
    return render_template(f"area_cliente/{page}")

@app.route('/site/<path:subpath>')
def site_template_proxy(subpath):
    """Renderiza qualquer template dentro de `templates/site/` se existir.
    Ex.: /site/categorias/velas.html -> templates/site/categorias/velas.html
    """
    # Segurança: só aceitar GET e checar existência do arquivo
    tpl_path = os.path.join(app.root_path, 'templates', 'site', subpath)
    if os.path.exists(tpl_path) and os.path.isfile(tpl_path):
        return render_template(f"site/{subpath}")
    else:
        from flask import abort
        abort(404)


@app.route('/<path:page>')
def site_page_proxy(page):
    """Renderiza templates `templates/site/<page>` quando existir (páginas no nível raiz).
    Ex.: /produtos.html -> templates/site/produtos.html
    """
    if not page.endswith('.html'):
        from flask import abort
        abort(404)
    tpl_path = os.path.join(app.root_path, 'templates', 'site', page)
    if os.path.exists(tpl_path) and os.path.isfile(tpl_path):
        return render_template(f"site/{page}")
    else:
        from flask import abort
        abort(404)


if __name__ == "__main__":
    app.run(debug=True, port=5000)