from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta_lume_essence'  # Necessário para sessões (login)

# --- Conexão com Banco ---
def get_db():
    conn = sqlite3.connect("db_lume.db")
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    return conn

# --- Rotas Públicas ---
@app.route("/")
def index():
    return render_template("site/index.html")

@app.route("/produtos")
def produtos():
    return render_template("site/produtos.html")

@app.route("/sobre")
def sobre():
    return render_template("site/sobre.html")

@app.route("/contato")
def contato():
    return render_template("site/contato.html")

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
def login_page():
    return render_template("site/login.html")

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
    
    return redirect("/area-cliente/area-cliente.html") # Ajuste a rota conforme necessário

# --- Carrinho e Checkout ---
@app.route("/carrinho")
def carrinho():
    return render_template("site/carrinho.html")

@app.route("/checkout")
def checkout():
    # Verifica se está logado (Simples)
    # if 'user_id' not in session:
    #     return redirect("/login")
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
    qtd_parcelas = request.form.get("parcelas_escolhidas", 1)
    
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

                cur.execute("""
                    INSERT INTO tb_cartoes (id_cliente, nome_titular, ultimos_4, bandeira, token_pagamento, validade)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id_cliente, nome_titular, ultimos_4, bandeira, token_falso, validade))

        # 2. Salvar Pedido
        data_atual = datetime.now()
        data_entrega = datetime.now() # Adicione dias se quiser

        # Certifique-se que a coluna 'parcelas' existe no banco
        cur.execute("""
            INSERT INTO tb_pedidos (id_cliente, data_pedido, status, valor_total, data_entrega, forma_pagamento, parcelas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_cliente, data_atual, 'Pendente', valor_total, data_entrega, forma_pagamento, qtd_parcelas))
        
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
    # Aqui você faria um SELECT no banco para mostrar os pedidos reais
    return render_template("area_cliente/meus-pedidos.html")

# Demais rotas da área do cliente (favoritos, endereços, etc)...
@app.route("/area_cliente/<page>")
def area_cliente_pages(page):
    return render_template(f"area_cliente/{page}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)