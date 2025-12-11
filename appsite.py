from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta_lume_essence'  # Necessário para o carrinho e login

# --- Configuração do Banco de Dados ---
def get_db():
    conn = sqlite3.connect("db_lume.db")
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome (ex: item['nome'])
    return conn

# --- Processador de Contexto (Injeta variáveis em todos os templates) ---
@app.context_processor
def inject_cart_count():
    total_itens = 0
    if 'carrinho' in session:
        for item in session['carrinho']:
            total_itens += item['qtd']
    return dict(cart_count=total_itens)

# --- Rotas Públicas (Com alias .html para evitar erros 404) ---
@app.route("/")
@app.route("/index.html")
def index():
    return render_template("site/index.html")

@app.route("/produtos")
@app.route("/produtos.html")
def produtos():
    con = get_db()
    cur = con.cursor()
    # Busca produtos ativos
    cur.execute("SELECT * FROM tb_produtos")
    lista_produtos = cur.fetchall()
    con.close()
    return render_template("site/produtos.html", produtos=lista_produtos)

@app.route("/produto/<int:id_produto>")
@app.route("/produto-detalhe.html") # Rota legado
def produto_detalhe(id_produto=None):
    if not id_produto:
        # Se acessou direto pelo html antigo, redireciona ou mostra erro
        return redirect("/produtos")
        
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_produtos WHERE id_produto = ?", (id_produto,))
    produto = cur.fetchone()
    con.close()
    
    if produto:
        return render_template("site/produto-detalhe.html", produto=produto)
    return "Produto não encontrado", 404

@app.route("/sobre")
@app.route("/sobre.html")
def sobre():
    return render_template("site/sobre.html")

@app.route("/contato")
@app.route("/contato.html")
def contato():
    return render_template("site/contato.html")

@app.route("/contato/enviar", methods=["POST"])
def enviar_contato():
    nome = request.form.get("nome")
    email = request.form.get("email")
    tel_cel = request.form.get("tel_cel")
    mensagem = request.form.get("mensagem")
    data_contato = datetime.now()

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO tb_contatos (nome, email, tel_cel, mensagem, data_contato) VALUES (?, ?, ?, ?, ?)",
                    (nome, email, tel_cel, mensagem, data_contato))
        con.commit()
    except Exception as e:
        print(f"Erro ao salvar contato: {e}")
    finally:
        con.close()
    return redirect("/contato")

# --- Newsletter ---
@app.route("/newsletter/cadastrar", methods=["POST"])
def cadastrar_newsletter():
    nome = request.form.get("nome")
    whatsapp = request.form.get("whatsapp")
    email = request.form.get("email")
    data_cad = datetime.now()

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO tb_newsletter (nome, whatsapp, email, data_cad) VALUES (?, ?, ?, ?)",
                    (nome, whatsapp, email, data_cad))
        con.commit()
    except:
        pass 
    con.close()
    return redirect("/")

# --- Autenticação e Cadastro ---
@app.route("/login")
@app.route("/site/login.html")
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
    nome = request.form.get("nome")
    data_nasc = request.form.get("data_nasc")
    cpf = request.form.get("cpf")
    genero = request.form.get("genero")
    tel_cel = request.form.get("tel_cel")
    email = request.form.get("email")
    cep = request.form.get("cep")
    endereco = request.form.get("endereco")
    n = request.form.get("n")
    complemento = request.form.get("complemento", "")
    referencia = request.form.get("referencia", "")
    bairro = request.form.get("bairro")
    cidade = request.form.get("cidade")
    estado = request.form.get("estado")
    senha = request.form.get("senha")
    data_cad = datetime.now()

    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO tb_clientes (nome, data_nasc, cpf, genero, tel_cel, email, cep, endereco, n, complemento, referencia, bairro, cidade, estado, senha, data_cad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, data_nasc, cpf, genero, tel_cel, email, cep, endereco, n, complemento, referencia, bairro, cidade, estado, senha, data_cad))
    con.commit()
    
    # Auto Login
    session['user_id'] = cur.lastrowid
    session['user_nome'] = nome
    con.close()
    
    return redirect("/area_cliente/area-cliente.html")

# --- Carrinho de Compras ---
@app.route("/carrinho")
@app.route("/site/carrinho.html")
def carrinho():
    if 'carrinho' not in session or len(session['carrinho']) == 0:
        return render_template("site/carrinho.html", itens=[], total=0)
    
    carrinho_sessao = session['carrinho']
    itens_completos = []
    total_geral = 0

    con = get_db()
    cur = con.cursor()

    for item in carrinho_sessao:
        cur.execute("SELECT * FROM tb_produtos WHERE id_produto = ?", (item['id'],))
        produto = cur.fetchone()
        
        if produto:
            subtotal = produto['preco_venda'] * item['qtd']
            total_geral += subtotal
            
            itens_completos.append({
                'id': produto['id_produto'],
                'nome': produto['nome_produto'],
                'imagem': produto['img_produto'],
                'preco': produto['preco_venda'],
                'qtd': item['qtd'],
                'subtotal': subtotal
            })
    con.close()
    return render_template("site/carrinho.html", itens=itens_completos, total=total_geral)

@app.route("/adicionar-carrinho/<int:id_produto>")
def adicionar_carrinho(id_produto):
    if 'carrinho' not in session:
        session['carrinho'] = []

    encontrado = False
    for item in session['carrinho']:
        if item['id'] == id_produto:
            item['qtd'] += 1
            encontrado = True
            break
    
    if not encontrado:
        session['carrinho'].append({'id': id_produto, 'qtd': 1})
    
    session.modified = True
    return redirect("/carrinho")

@app.route("/remover-carrinho/<int:id_produto>")
def remover_carrinho(id_produto):
    if 'carrinho' in session:
        session['carrinho'] = [item for item in session['carrinho'] if item['id'] != id_produto]
        session.modified = True
    return redirect("/carrinho")

@app.route("/alterar-qtd/<int:id_produto>/<acao>")
def alterar_qtd(id_produto, acao):
    if 'carrinho' in session:
        for item in session['carrinho']:
            if item['id'] == id_produto:
                if acao == 'mais':
                    item['qtd'] += 1
                elif acao == 'menos' and item['qtd'] > 1:
                    item['qtd'] -= 1
                break
        session.modified = True
    return redirect("/carrinho")

# --- Checkout e Pedidos ---
@app.route("/checkout")
def checkout():
    # if 'user_id' not in session: return redirect("/login")
    return render_template("site/checkout.html")

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    # Pega ID do usuário logado ou usa 1 para teste
    id_cliente = session.get('user_id', 1) 
    
    valor_total = request.form.get("total_pedido")
    forma_pagamento = request.form.get("forma_pagamento")
    lista_itens_json = request.form.get("lista_itens")
    qtd_parcelas = request.form.get("parcelas_escolhidas", 1)
    
    con = get_db()
    cur = con.cursor()

    try:
        # 1. Lógica do Cartão (Salvar se solicitado)
        if forma_pagamento == 'credit':
            save_option = request.form.get("save_card_option", "nao")
            card_number = request.form.get("card_number_sent", "")
            
            if save_option == 'sim' and card_number:
                nome_titular = request.form.get("card_holder_sent")
                validade = request.form.get("card_expiry_sent")
                ultimos_4 = card_number.replace(" ", "")[-4:]
                bandeira = "Visa" if card_number.startswith("4") else "Mastercard"
                token_falso = str(uuid.uuid4())

                try:
                    cur.execute("""
                        INSERT INTO tb_cartoes (id_cliente, nome_titular, ultimos_4, bandeira, token_pagamento, validade)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (id_cliente, nome_titular, ultimos_4, bandeira, token_falso, validade))
                except Exception as e:
                    print(f"Erro ao salvar cartão (tabela pode não existir): {e}")

        # 2. Salvar Pedido
        data_atual = datetime.now()
        data_entrega = datetime.now() 

        # Verifica se tabela tem coluna parcelas, senão ignora (Fallback de segurança)
        try:
            cur.execute("""
                INSERT INTO tb_pedidos (id_cliente, data_pedido, status, valor_total, data_entrega, forma_pagamento, parcelas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_cliente, data_atual, 'Pendente', valor_total, data_entrega, forma_pagamento, qtd_parcelas))
        except:
             cur.execute("""
                INSERT INTO tb_pedidos (id_cliente, data_pedido, status, valor_total, data_entrega, forma_pagamento)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_cliente, data_atual, 'Pendente', valor_total, data_entrega, forma_pagamento))
        
        id_novo_pedido = cur.lastrowid 

        # 3. Salvar Itens
        if lista_itens_json:
            itens = json.loads(lista_itens_json)
            for item in itens:
                subtotal = float(item['qtd']) * float(item['preco'])
                cur.execute("""
                    INSERT INTO tb_itensPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_novo_pedido, item['id_produto'], item['qtd'], item['preco'], subtotal))

        # --- 4. NOVO: LANÇAMENTO AUTOMÁTICO NO FINANCEIRO (RECEITA) ---
        
        # Define status: Se for Pix ou Cartão, já entra como "Recebido". Se fosse Boleto, seria "Pendente".
        status_financeiro = 'Recebido'
        
        # Cria a descrição automática (Ex: "Venda Site #5420 - Cliente X")
        # Nota: Idealmente buscaríamos o nome do cliente, mas aqui usamos o ID para ser rápido
        descricao_lancamento = f"Venda E-commerce Pedido #{id_novo_pedido}"
        
        cur.execute("""
            INSERT INTO tb_contasReceber (descricao, valor, data_emissao, data_venc, categoria, status, id_pedido, id_cliente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (descricao_lancamento, valor_total, data_atual, data_atual, "Venda Online", status_financeiro, id_novo_pedido, id_cliente))
        
        print(f"💰 Venda #{id_novo_pedido} lançada no financeiro com sucesso!")
        # -------------------------------------------------------------

        con.commit()
        
        # Limpa o carrinho
        session['carrinho'] = []
        session.modified = True
        
        return redirect("/area_cliente/meus-pedidos.html")

    except Exception as e:
        con.rollback()
        print(f"Erro Crítico no Checkout: {e}")
        return f"Erro ao processar pedido: {e}"
    finally:
        con.close()

        
# --- Área do Cliente ---
@app.route("/area_cliente/area-cliente.html")
def area_cliente_home():
    return render_template("area_cliente/area-cliente.html")

@app.route("/area_cliente/meus-pedidos.html")
def area_cliente_pedidos():
    id_cliente = session.get('user_id', 1)
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_pedidos WHERE id_cliente = ? ORDER BY data_pedido DESC", (id_cliente,))
    pedidos = cur.fetchall()
    con.close()
    return render_template("area_cliente/meus-pedidos.html", pedidos=pedidos)

@app.route("/area_cliente/favoritos.html")
def area_favoritos():
    return render_template("area_cliente/favoritos.html")

@app.route("/area_cliente/enderecos.html")
def area_enderecos():
    return render_template("area_cliente/enderecos.html")

@app.route("/area_cliente/cartoes.html")
def area_cartoes():
    # Opcional: Buscar cartões do banco para mostrar
    return render_template("area_cliente/cartoes.html")

@app.route("/area_cliente/meus-dados.html")
def area_dados():
    return render_template("area_cliente/meus-dados.html")

# Inicialização
if __name__ == "__main__":
    app.run(debug=True, port=5000)