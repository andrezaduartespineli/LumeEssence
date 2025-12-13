from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import json
import uuid
import math
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)
app.secret_key = 'chave_secreta_lume_essence'  # Necessário para o carrinho e login

# Coloque isso logo após criar o 'app = Flask(__name__)'
import os
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER_PERFIL = os.path.join(BASE_DIR, 'static', 'uploads', 'perfil')
app.config['UPLOAD_FOLDER_PERFIL'] = UPLOAD_FOLDER_PERFIL
os.makedirs(UPLOAD_FOLDER_PERFIL, exist_ok=True)

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
    con = get_db()
    cur = con.cursor()
    
    # 1. Busca os Lançamentos (3 últimos cadastrados)
    cur.execute("SELECT * FROM tb_produtos WHERE ativo = 1 ORDER BY id_produto DESC LIMIT 3")
    lancamentos = cur.fetchall()

    # 2. Busca os Mais Vendidos (Top 8)
    # Essa consulta soma a quantidade vendida de cada item. 
    # Se o produto nunca foi vendido, o COALESCE garante que o total seja 0.
    # Ordena pelo total de vendas (maior para menor).
    cur.execute("""
        SELECT p.*, COALESCE(SUM(ip.quantidade), 0) as total_vendas
        FROM tb_produtos p
        LEFT JOIN tb_itensPedido ip ON p.id_produto = ip.id_produto
        WHERE p.ativo = 1
        GROUP BY p.id_produto
        ORDER BY total_vendas DESC, p.id_produto DESC
        LIMIT 8
    """)
    mais_vendidos = cur.fetchall()
    
    con.close()
    
    return render_template("site/index.html", 
                           lancamentos=lancamentos, 
                           mais_vendidos=mais_vendidos)

@app.route("/produtos")
@app.route("/produtos.html")
def produtos():
    ITENS_POR_PAGINA = 15
    
    # Captura Parâmetros
    pagina_atual = request.args.get('page', 1, type=int)
    ordem_atual = request.args.get('ordem', 'padrao')
    
    # Filtros laterais
    cat_filtro = request.args.get('categoria')
    aromas_filtro = request.args.getlist('aroma') 
    variacoes_filtro = request.args.getlist('variacao')
    novidades_filtro = request.args.get('novidades') 
    
    # --- NOVO: Captura o texto da busca ---
    termo_busca = request.args.get('q') 
    
    con = get_db()
    cur = con.cursor()
    
    # Query Base
    sql_base = "SELECT * FROM tb_produtos WHERE ativo = 1"
    sql_count = "SELECT COUNT(*) FROM tb_produtos WHERE ativo = 1"
    
    filtros_sql = []
    parametros = []
    
    # 1. Filtro de Busca (Texto)
    if termo_busca:
        # Procura no Nome OU na Descrição (o % serve para buscar em qualquer parte do texto)
        filtros_sql.append("(nome_produto LIKE ? OR descricao LIKE ?)")
        parametros.append(f'%{termo_busca}%')
        parametros.append(f'%{termo_busca}%')

    # 2. Outros Filtros
    if novidades_filtro == 'true':
        filtros_sql.append("data_cad >= date('now', '-45 days')")

    if cat_filtro:
        filtros_sql.append("categoria = ?")
        parametros.append(cat_filtro)
        
    if aromas_filtro:
        placeholders = ','.join(['?'] * len(aromas_filtro)) 
        filtros_sql.append(f"aroma IN ({placeholders})")
        parametros.extend(aromas_filtro)

    if variacoes_filtro:
        placeholders = ','.join(['?'] * len(variacoes_filtro))
        filtros_sql.append(f"variacao IN ({placeholders})")
        parametros.extend(variacoes_filtro)

    if filtros_sql:
        clausula_where = " AND " + " AND ".join(filtros_sql)
        sql_base += clausula_where
        sql_count += clausula_where

    # 3. Ordenação e Paginação
    if novidades_filtro == 'true' and ordem_atual == 'padrao':
        sql_base += " ORDER BY data_cad DESC, id_produto DESC"
    elif ordem_atual == 'menor_preco':
        sql_base += " ORDER BY preco_venda ASC"
    elif ordem_atual == 'maior_preco':
        sql_base += " ORDER BY preco_venda DESC"
    elif ordem_atual == 'az':
        sql_base += " ORDER BY nome_produto ASC"
    elif ordem_atual == 'za':
        sql_base += " ORDER BY nome_produto DESC"
    else:
        sql_base += " ORDER BY id_produto DESC"

    # Define limite de paginação
    if novidades_filtro == 'true':
        limit = 6; offset = 0; total_paginas = 1 
    else:
        limit = 15; offset = (pagina_atual - 1) * limit
        cur.execute(sql_count, parametros)
        total_produtos = cur.fetchone()[0]
        total_paginas = math.ceil(total_produtos / limit)
    
    sql_base += " LIMIT ? OFFSET ?"
    parametros.append(limit)
    parametros.append(offset)
    
    cur.execute(sql_base, parametros)
    lista_produtos = cur.fetchall()
    con.close()
    
    return render_template("site/produtos.html", 
                           produtos=lista_produtos, 
                           pagina_atual=pagina_atual, 
                           total_paginas=total_paginas,
                           ordem_atual=ordem_atual,
                           aromas_selecionados=aromas_filtro,
                           variacoes_selecionadas=variacoes_filtro,
                           cat_selecionada=cat_filtro,
                           eh_novidade=novidades_filtro,
                           termo_busca=termo_busca) # Devolve o texto para manter na caixinha
    
@app.route("/produto/<int:id_produto>")
def produto_detalhe(id_produto):
    con = get_db()
    cur = con.cursor()
    
    # 1. Busca o produto principal
    cur.execute("SELECT * FROM tb_produtos WHERE id_produto = ?", (id_produto,))
    produto = cur.fetchone()
    
    if not produto:
        con.close()
        return "Produto não encontrado", 404
    
    # 2. Busca produtos relacionados (para a sugestão no final da página)
    cur.execute("""
        SELECT * FROM tb_produtos 
        WHERE categoria = ? AND id_produto != ? AND ativo = 1 
        ORDER BY RANDOM() LIMIT 4
    """, (produto['categoria'], id_produto))
    relacionados = cur.fetchall()
    
    con.close()
    
    # Enviamos 'p' (produto abreviado) para funcionar com seu HTML
    return render_template("site/produto-detalhe.html", p=produto, relacionados=relacionados)


# --- Rotas de Páginas Institucionais ---
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
    print("--- Recebendo formulário de contato ---")
    
    # 1. Recebe os dados do HTML
    nome = request.form.get("nome")
    email = request.form.get("email")
    tel_cel = request.form.get("tel_cel")
    mensagem = request.form.get("mensagem")
    data_contato = datetime.now()

    con = get_db()
    cur = con.cursor()

    try:
        # 2. Tenta salvar no banco
        cur.execute("""
            INSERT INTO tb_contatos (nome, email, tel_cel, mensagem, data_contato) 
            VALUES (?, ?, ?, ?, ?)
        """, (nome, email, tel_cel, mensagem, data_contato))
        
        con.commit()
        print("✅ Mensagem salva com sucesso!")
        
        # Opcional: Você pode criar uma página de "obrigado.html" ou só recarregar
        return redirect("/contato") 

    except Exception as e:
        con.rollback()
        print(f"❌ ERRO AO SALVAR CONTATO: {e}")
        return f"Erro ao enviar mensagem: {e}"
    finally:
        con.close()
        
# --- Newsletter ---
@app.route("/newsletter/cadastrar", methods=["POST"])
def cadastrar_newsletter():
    # Recebe os dados (pode vir vazio se o form não tiver o campo)
    nome = request.form.get("nome", "Anônimo")
    whatsapp = request.form.get("whatsapp", "")
    email = request.form.get("email")
    data_cad = datetime.now()

    print(f"--- Tentando cadastrar Newsletter: {email} ---") # Log no terminal

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO tb_newsletter (nome, whatsapp, email, data_cad) 
            VALUES (?, ?, ?, ?)
        """, (nome, whatsapp, email, data_cad))
        con.commit()
        print("✅ Sucesso! Lead salvo no banco.")
    except Exception as e:
        con.rollback()
        print(f"❌ ERRO AO SALVAR NEWSLETTER: {e}") # Isso vai te dizer o problema exato
    finally:
        con.close()
        
    # Redireciona de volta para a Home
    return redirect("/")


# --- Autenticação e Cadastro ---
# ==========================================
# ROTA DE LOGIN (CORRETA E COMPLETA)
# ==========================================
# 1. Rota de Login (GET para ver a página, POST para entrar)
@app.route("/login", methods=['GET', 'POST'])
@app.route("/site/login.html")
def login_cliente():
    # Se já estiver logado, manda pra Área do Cliente
    if 'id_cliente' in session:
        return redirect("/area_cliente/area-cliente.html")

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM tb_clientes WHERE email = ?", (email,))
        usuario = cur.fetchone()
        con.close()
        
        # Verifica se o usuário existe e se a senha bate (Criptografada)
        if usuario and check_password_hash(usuario['senha'], senha):
            session['id_cliente'] = usuario['id_cliente']
            session['nome_cliente'] = usuario['nome'].split()[0]
            return redirect("/") # Sucesso! Vai pra Home
        else:
            return render_template("site/login.html", erro="E-mail ou senha incorretos.")

    return render_template("site/login.html")

# 2. Rota para exibir a página de Cadastro
@app.route("/cadastro-cliente", methods=['GET'])
def pagina_cadastro():
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

# 3. Rota que recebe os dados do Cadastro e Salva no Banco
# Rota que Recebe os Dados do Cadastro (POST)
@app.route("/cadastro-cliente", methods=['POST'])
def cadastrar_cliente_post():
    # Coleta todos os campos do formulário
    nome = request.form['nome']
    data_nasc = request.form['data_nasc']
    genero = request.form['genero']
    tel_cel = request.form['tel_cel']
    email = request.form['email']
    cpf = request.form['cpf']
    cep = request.form['cep']
    endereco = request.form['endereco']
    numero = request.form['n']
    complemento = request.form['complemento']
    referencia = request.form['referencia']
    bairro = request.form['bairro']
    cidade = request.form['cidade']
    estado = request.form['estado']
    senha = request.form['senha']
    
    # Campo de verificação
    confirma_senha = request.form.get('confirma_senha') 

    # 1. Validação no Python
    if senha != confirma_senha:
         return render_template("site/cadastro.html", erro="As senhas não coincidem.")

    # 2. Criptografia
    senha_hash = generate_password_hash(senha)
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Verifica se e-mail já existe
        cur.execute("SELECT id_cliente FROM tb_clientes WHERE email = ?", (email,))
        if cur.fetchone():
            con.close()
            return render_template("site/cadastro.html", erro="Este e-mail já está em uso.")
        
        # 3. Insere no Banco (AGORA INCLUINDO confirmar_senha)
        cur.execute("""
            INSERT INTO tb_clientes 
            (nome, data_nasc, cpf, genero, tel_cel, email, cep, endereco, n, complemento, referencia, bairro, cidade, estado, senha, confirmar_senha) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, data_nasc, cpf, genero, tel_cel, email, cep, endereco, numero, complemento, referencia, bairro, cidade, estado, senha_hash, senha_hash))
        
        con.commit()
        
        # Login Automático
        cur.execute("SELECT * FROM tb_clientes WHERE email = ?", (email,))
        usuario = cur.fetchone()
        session['id_cliente'] = usuario['id_cliente']
        session['nome_cliente'] = usuario['nome'].split()[0]
        
        con.close()
        return redirect("/")
        
    except Exception as e:
        con.close()
        return f"Erro no banco de dados: {e}"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# --- ROTA: ENVIAR E-MAIL EM MASSA ---
@app.route("/admin/newsletter/enviar", methods=['POST'])
def enviar_email_massa():
    if 'id_usuario' not in session: return redirect("/admin/login") # Proteção de admin

    # 1. Pega a lista de e-mails selecionados (checkboxes)
    lista_destinatarios = request.form.getlist('emails_selecionados')
    assunto_texto = request.form['assunto']
    corpo_mensagem = request.form['mensagem']

    if not lista_destinatarios:
        flash("Selecione pelo menos um e-mail!", "erro")
        return redirect("/admin/newsletter")

    # 2. Configurações do seu E-mail (GMAIL Exemplo)
    MEU_EMAIL = "seu_email@gmail.com"
    MINHA_SENHA = "sua_senha_de_app_aqui" # Gere uma senha de app no Google
    SERVIDOR_SMTP = "smtp.gmail.com"
    PORTA_SMTP = 587

    try:
        # Conecta ao servidor de e-mail
        server = smtplib.SMTP(SERVIDOR_SMTP, PORTA_SMTP)
        server.starttls()
        server.login(MEU_EMAIL, MINHA_SENHA)

        # 3. Loop para enviar um por um
        for dest in lista_destinatarios:
            msg = MIMEMultipart()
            msg['From'] = MEU_EMAIL
            msg['To'] = dest
            msg['Subject'] = assunto_texto

            # Adiciona o texto da mensagem
            msg.attach(MIMEText(corpo_mensagem, 'plain'))

            # Envia
            server.sendmail(MEU_EMAIL, dest, msg.as_string())

        server.quit()
        flash(f"Sucesso! E-mail enviado para {len(lista_destinatarios)} pessoas.", "sucesso")

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        flash("Erro ao enviar e-mails. Verifique as configurações no console.", "erro")

    return redirect("/admin/newsletter")

# --- Carrinho de Compras ---
# --- ROTAS COMPLETAS DO CARRINHO ---

@app.route("/adicionar-carrinho/<int:id_produto>")
def adicionar_carrinho(id_produto):
    # 1. Busca os dados completos do produto no banco
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_produtos WHERE id_produto = ?", (id_produto,))
    produto_db = cur.fetchone()
    con.close()
    
    if not produto_db:
        return "Produto não encontrado", 404

    # 2. Prepara os dados para salvar na sessão
    preco = float(produto_db['preco_venda'])
    
    # Cria a estrutura do item
    novo_item = {
        'id': produto_db['id_produto'],
        'nome': produto_db['nome_produto'],
        'preco': preco,
        'imagem': produto_db['img_produto'],
        'sku': produto_db['sku'],
        'qtd': 1,
        'subtotal': preco
    }

    # 3. Gerencia a Sessão
    if 'carrinho' not in session:
        session['carrinho'] = []

    carrinho_atual = session['carrinho']
    encontrou = False

    # Se já existe, só aumenta a quantidade
    for item in carrinho_atual:
        if item['id'] == id_produto:
            item['qtd'] += 1
            item['subtotal'] = item['qtd'] * item['preco']
            encontrou = True
            break

    if not encontrou:
        carrinho_atual.append(novo_item)

    session['carrinho'] = carrinho_atual
    session.modified = True
    
    return redirect("/carrinho")

@app.route("/carrinho")
@app.route("/carrinho.html")
def ver_carrinho():
    carrinho = session.get('carrinho', [])
    
    # Recalcula totais para garantir
    total_geral = 0
    for item in carrinho:
        item['subtotal'] = item['qtd'] * item['preco']
        total_geral += item['subtotal']
        
    return render_template("site/carrinho.html", carrinho=carrinho, total_geral=total_geral)

@app.route("/remover-carrinho/<int:id_produto>")
def remover_carrinho(id_produto):
    if 'carrinho' in session:
        # Recria a lista removendo o item selecionado
        session['carrinho'] = [item for item in session['carrinho'] if item['id'] != id_produto]
        session.modified = True
    return redirect("/carrinho")

@app.route("/limpar-carrinho")
def limpar_carrinho():
    session.pop('carrinho', None)
    return redirect("/carrinho")

# Rota Extra: Botões de + e - no carrinho (Opcional, mas útil)
@app.route("/alterar-qtd/<int:id_produto>/<acao>")
def alterar_qtd(id_produto, acao):
    if 'carrinho' in session:
        for item in session['carrinho']:
            if item['id'] == id_produto:
                if acao == 'mais':
                    item['qtd'] += 1
                elif acao == 'menos' and item['qtd'] > 1:
                    item['qtd'] -= 1
                item['subtotal'] = item['qtd'] * item['preco']
                break
        session.modified = True
    return redirect("/carrinho")

# --- Checkout e Pedidos ---
# --- ROTA DE CHECKOUT ---
@app.route("/checkout")
def checkout():
    # 1. Segurança: Se não tem carrinho, manda voltar para produtos
    if 'carrinho' not in session or not session['carrinho']:
        return redirect("/produtos")
    
    carrinho = session['carrinho']
    
    # 2. Calcula o Total Geral
    total_geral = sum(item['subtotal'] for item in carrinho)
    
    # 3. Renderiza a tela passando os dados
    return render_template("site/checkout.html", 
                           carrinho=carrinho, 
                           total_geral=total_geral)

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    id_cliente = session.get('user_id', 1) 
    valor_total = request.form.get("total_pedido")
    forma_pagamento = request.form.get("forma_pagamento")
    lista_itens_json = request.form.get("lista_itens")
    qtd_parcelas = request.form.get("parcelas_escolhidas", 1)
    
    con = get_db()
    cur = con.cursor()

    try:
        # 1. Salvar Cartão (Se solicitado)
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
                    cur.execute("INSERT INTO tb_cartoes (id_cliente, nome_titular, ultimos_4, bandeira, token_pagamento, validade) VALUES (?, ?, ?, ?, ?, ?)", 
                                (id_cliente, nome_titular, ultimos_4, bandeira, token_falso, validade))
                except: pass

        # 2. Salvar Pedido
        data_atual = datetime.now()
        cur.execute("""
            INSERT INTO tb_pedidos (id_cliente, data_pedido, status, valor_total, data_entrega, forma_pagamento, parcelas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_cliente, data_atual, 'Pendente', valor_total, data_atual, forma_pagamento, qtd_parcelas))
        id_novo_pedido = cur.lastrowid 

        # 3. Salvar Itens
        if lista_itens_json:
            itens = json.loads(lista_itens_json)
            for item in itens:
                subtotal = float(item['qtd']) * float(item['preco'])
                cur.execute("INSERT INTO tb_itensPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)", 
                            (id_novo_pedido, item['id_produto'], item['qtd'], item['preco'], subtotal))

        # --- 4. NOVO: LANÇAR NO FINANCEIRO AUTOMATICAMENTE ---
        status_fin = 'Recebido' # Assume recebido para Pix/Cartão
        cur.execute("""
            INSERT INTO tb_contasReceber (descricao, valor, data_emissao, data_venc, categoria, status, id_pedido, id_cliente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (f"Venda Site #{id_novo_pedido}", valor_total, data_atual, data_atual, "Venda Online", status_fin, id_novo_pedido, id_cliente))
        # -----------------------------------------------------

        con.commit()
        session['carrinho'] = []
        session.modified = True
        return redirect("/area_cliente/meus-pedidos.html")

    except Exception as e:
        con.rollback()
        print(f"Erro: {e}")
        return f"Erro: {e}"
    finally:
        con.close()
        
# --- Área do Cliente ---
# ==========================================
# ROTAS DA ÁREA DO CLIENTE (CORRIGIDAS)
# ==========================================

# 1. VISÃO GERAL (DASHBOARD)
@app.route("/area_cliente/area-cliente.html")
def area_cliente():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    con = get_db()
    cur = con.cursor()
    
    # Busca dados do Cliente
    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
    dados_cliente = cur.fetchone()
    
    # Proteção: Se cliente não existir (banco apagado), faz logout
    if not dados_cliente:
        session.clear()
        con.close()
        return redirect("/login")

    # Busca Histórico (5 últimos)
    cur.execute("SELECT * FROM tb_pedidos WHERE id_cliente = ? ORDER BY id_pedido DESC LIMIT 5", (id_cliente,))
    lista_pedidos = cur.fetchall()

    # Estatística: Em Trânsito
    cur.execute("SELECT COUNT(*) FROM tb_pedidos WHERE id_cliente = ? AND status = 'Enviado'", (id_cliente,))
    qtd_em_transito = cur.fetchone()[0]

    # Último Pedido (Destaque)
    ultimo_pedido = None
    item_destaque = None
    progresso = 0
    
    if lista_pedidos:
        ultimo_pedido = lista_pedidos[0]
        cur.execute("""
            SELECT p.nome_produto, p.img_produto, ip.quantidade, ip.preco_unitario
            FROM tb_itensPedido ip
            JOIN tb_produtos p ON ip.id_produto = p.id_produto
            WHERE ip.id_pedido = ? LIMIT 1
        """, (ultimo_pedido['id_pedido'],))
        item_destaque = cur.fetchone()

        status = ultimo_pedido['status']
        if status == 'Cancelado': progresso = 0
        elif status == 'Pendente': progresso = 1
        elif status == 'Aprovado': progresso = 2
        elif status == 'Separado': progresso = 3
        elif status == 'Enviado':  progresso = 4
        elif status == 'Entregue': progresso = 5

    con.close()
    return render_template("area_cliente/area-cliente.html", 
                           cliente=dados_cliente, 
                           pedidos=lista_pedidos,
                           ultimo_pedido=ultimo_pedido,
                           item_destaque=item_destaque,
                           qtd_em_transito=qtd_em_transito,
                           progresso=progresso)

# 2. MEUS PEDIDOS (LISTA COMPLETA)
# --- ROTA: MEUS PEDIDOS (COM FILTRO) ---
@app.route("/area_cliente/meus-pedidos.html")
def meus_pedidos():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    
    # Captura o filtro da URL (ex: ?status=entregue)
    filtro_status = request.args.get('status')

    con = get_db()
    cur = con.cursor()
    
    # Busca dados do cliente (para o menu lateral)
    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
    dados_cliente = cur.fetchone()

    # Monta a Query de Pedidos
    sql = "SELECT * FROM tb_pedidos WHERE id_cliente = ?"
    params = [id_cliente]

    # Aplica o filtro se houver
    if filtro_status == 'aberto':
        # Em aberto é tudo que NÃO está finalizado
        sql += " AND status NOT IN ('Entregue', 'Cancelado')"
    elif filtro_status == 'entregue':
        sql += " AND status = 'Entregue'"
    elif filtro_status == 'cancelado':
        sql += " AND status = 'Cancelado'"
    
    # Ordena do mais recente para o mais antigo
    sql += " ORDER BY id_pedido DESC"

    cur.execute(sql, params)
    lista_pedidos = cur.fetchall()
    
    con.close()
    
    # Envia 'status_atual' para o HTML saber qual botão pintar de ativo
    return render_template("area_cliente/meus-pedidos.html", 
                           cliente=dados_cliente, 
                           pedidos=lista_pedidos,
                           status_atual=filtro_status)

# 3. MEUS DADOS (EDITAR PERFIL + FOTO)
@app.route("/area_cliente/meus-dados.html", methods=['GET', 'POST'])
def meus_dados():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    con = get_db()
    cur = con.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        tel_cel = request.form['tel_cel']
        cep = request.form['cep']
        endereco = request.form['endereco']
        n = request.form['n']
        complemento = request.form['complemento']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']
        
        arquivo_foto = request.files.get('foto_perfil')
        
        if arquivo_foto and arquivo_foto.filename != '':
            filename = secure_filename(arquivo_foto.filename)
            nome_foto_final = f"{id_cliente}_{filename}"
            caminho = os.path.join(app.config['UPLOAD_FOLDER_PERFIL'], nome_foto_final)
            arquivo_foto.save(caminho)
            
            cur.execute("""
                UPDATE tb_clientes SET 
                nome=?, tel_cel=?, cep=?, endereco=?, n=?, complemento=?, bairro=?, cidade=?, estado=?, foto_perfil=?
                WHERE id_cliente=?
            """, (nome, tel_cel, cep, endereco, n, complemento, bairro, cidade, estado, nome_foto_final, id_cliente))
        else:
            cur.execute("""
                UPDATE tb_clientes SET 
                nome=?, tel_cel=?, cep=?, endereco=?, n=?, complemento=?, bairro=?, cidade=?, estado=?
                WHERE id_cliente=?
            """, (nome, tel_cel, cep, endereco, n, complemento, bairro, cidade, estado, id_cliente))

        con.commit()
        session['nome_cliente'] = nome.split()[0]
        con.close()
        return redirect("/area_cliente/meus-dados.html")

    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
    dados_cliente = cur.fetchone()
    con.close()
    
    return render_template("area_cliente/meus-dados.html", cliente=dados_cliente)

# 4. ENDEREÇOS (VISUALIZAR)
# --- ROTA: MEUS ENDEREÇOS (LISTAR) ---
@app.route("/area_cliente/enderecos.html")
def meus_enderecos():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    con = get_db()
    cur = con.cursor()
    
    # 1. Busca o endereço PRINCIPAL (da tabela de clientes)
    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
    cliente = cur.fetchone()

    # 2. Busca endereços ADICIONAIS (da nova tabela)
    cur.execute("SELECT * FROM tb_enderecos WHERE id_cliente = ?", (id_cliente,))
    enderecos_extras = cur.fetchall()
    
    con.close()
    
    return render_template("area_cliente/enderecos.html", 
                           cliente=cliente, 
                           enderecos_extras=enderecos_extras)

# --- ROTA: ADICIONAR NOVO ENDEREÇO ---
@app.route("/area_cliente/adicionar_endereco", methods=['POST'])
def adicionar_endereco():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    titulo = request.form['titulo']
    cep = request.form['cep']
    endereco = request.form['endereco']
    numero = request.form['numero']
    complemento = request.form['complemento']
    bairro = request.form['bairro']
    cidade = request.form['cidade']
    estado = request.form['estado']
    
    con = get_db()
    cur = con.cursor()
    
    cur.execute("""
        INSERT INTO tb_enderecos (id_cliente, titulo, cep, endereco, numero, complemento, bairro, cidade, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_cliente, titulo, cep, endereco, numero, complemento, bairro, cidade, estado))
    
    con.commit()
    con.close()
    
    return redirect("/area_cliente/enderecos.html")

# --- ROTA: REMOVER ENDEREÇO ---
@app.route("/area_cliente/remover_endereco/<int:id_endereco>")
def remover_endereco(id_endereco):
    if 'id_cliente' not in session: return redirect("/login")
    
    con = get_db()
    cur = con.cursor()
    
    # Garante que só deleta se pertencer ao cliente logado (Segurança)
    cur.execute("DELETE FROM tb_enderecos WHERE id_endereco = ? AND id_cliente = ?", (id_endereco, session['id_cliente']))
    
    con.commit()
    con.close()
    
    return redirect("/area_cliente/enderecos.html")

# 5. FAVORITOS (PLACEHOLDER)
@app.route("/area_cliente/favoritos.html")
def meus_favoritos():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
    dados_cliente = cur.fetchone()
    con.close()
    
    return render_template("area_cliente/favoritos.html", cliente=dados_cliente)

# 6. CARTÕES (PLACEHOLDER)
# --- ROTA: MEUS CARTÕES (LISTAR) ---
@app.route("/area_cliente/cartoes.html")
def meus_cartoes():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    con = get_db()
    cur = con.cursor()
    
    # Busca dados do cliente (para sidebar)
    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
    dados_cliente = cur.fetchone()

    # Busca os cartões salvos
    cur.execute("SELECT * FROM tb_cartoes WHERE id_cliente = ?", (id_cliente,))
    lista_cartoes = cur.fetchall()
    
    con.close()
    
    return render_template("area_cliente/cartoes.html", 
                           cliente=dados_cliente, 
                           cartoes=lista_cartoes)

# --- ROTA: ADICIONAR CARTÃO ---
@app.route("/area_cliente/adicionar_cartao", methods=['POST'])
def adicionar_cartao():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    nome = request.form['nome_titular']
    numero_completo = request.form['numero_cartao']
    validade = request.form['validade']
    
    # 1. Pega apenas os últimos 4 dígitos para salvar
    numero_final = numero_completo[-4:]
    
    # 2. Identifica a bandeira simples (Lógica básica para visual)
    # Se começar com 4 é Visa, 5 é Master (simplificado)
    bandeira = 'visa' if numero_completo.startswith('4') else 'mastercard'
    if numero_completo.startswith('3'): bandeira = 'amex'
    
    con = get_db()
    cur = con.cursor()
    
    cur.execute("""
        INSERT INTO tb_cartoes (id_cliente, nome_titular, numero_final, bandeira, validade)
        VALUES (?, ?, ?, ?, ?)
    """, (id_cliente, nome, numero_final, bandeira, validade))
    
    con.commit()
    con.close()
    
    return redirect("/area_cliente/cartoes.html")

# --- ROTA: REMOVER CARTÃO ---
@app.route("/area_cliente/remover_cartao/<int:id_cartao>")
def remover_cartao(id_cartao):
    if 'id_cliente' not in session: return redirect("/login")
    
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM tb_cartoes WHERE id_cartao = ? AND id_cliente = ?", (id_cartao, session['id_cliente']))
    con.commit()
    con.close()
    
    return redirect("/area_cliente/cartoes.html")

# --- INJETOR DE CONTEXTO (Faz o carrinho funcionar em todas as páginas) ---
@app.context_processor
def inject_carrinho_global():
    # Pega o carrinho da sessão
    carrinho_atual = session.get('carrinho', [])
    
    # Conta quantos itens tem no total (Soma as quantidades)
    # Ex: Se comprou 2 velas e 1 spray, mostra "3"
    total_itens = sum(item['qtd'] for item in carrinho_atual)
    
    # Disponibiliza a variável 'qtd_carrinho' para todos os HTMLs
    return dict(qtd_carrinho=total_itens)

@app.context_processor
def inject_usuario():
    # Envia 'user_nome' se estiver logado, senão envia None
    return dict(user_nome=session.get('nome_cliente'))

# Inicialização
if __name__ == "__main__":
    app.run(debug=True, port=5000)