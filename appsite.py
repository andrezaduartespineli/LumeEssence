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

    # --- NOVO: BUSCA OS FAVORITOS DO CLIENTE ---
    ids_favoritos = [] # Começa vazio para não dar erro se não estiver logado
    
    if 'id_cliente' in session:
        user_id = session['id_cliente']
        # Pega a lista de IDs que esse cliente curtiu
        cur.execute("SELECT id_produto FROM tb_favoritos WHERE id_cliente = ?", (user_id,))
        # Transforma o resultado do banco em uma lista simples: [1, 5, 12]
        ids_favoritos = [item[0] for item in cur.fetchall()]
    # -------------------------------------------
    
    con.close()
    
    return render_template("site/index.html", 
                           lancamentos=lancamentos, 
                           mais_vendidos=mais_vendidos,
                           ids_favoritos=ids_favoritos) # <--- O SEGREDINHO AQUI NO FINAL

# --- ROTAS INSTITUCIONAIS ---

@app.route("/institucional")
@app.route("/institucional.html")
def institucional():
    return render_template("site/institucional.html")

@app.route("/rastreio")
@app.route("/rastreio.html")
def rastreio():
    return render_template("site/rastreio.html")

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
    
    # Busca por texto
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

    # 3. Ordenação
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

    # 4. Paginação
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

    # --- NOVO TRECHO: BUSCA OS FAVORITOS DO CLIENTE ---
    # Isto estava a faltar nesta função principal!
    ids_favoritos = []
    if 'id_cliente' in session:
        user_id = session['id_cliente']
        cur.execute("SELECT id_produto FROM tb_favoritos WHERE id_cliente = ?", (user_id,))
        ids_favoritos = [item[0] for item in cur.fetchall()]
    # --------------------------------------------------

    con.close()
    
    # 5. Retorno com ids_favoritos
    return render_template("site/produtos.html", 
                           produtos=lista_produtos, 
                           pagina_atual=pagina_atual, 
                           total_paginas=total_paginas,
                           ordem_atual=ordem_atual,
                           aromas_selecionados=aromas_filtro,
                           variacoes_selecionadas=variacoes_filtro,
                           cat_selecionada=cat_filtro,
                           eh_novidade=novidades_filtro,
                           termo_busca=termo_busca,
                           ids_favoritos=ids_favoritos) # <--- O SEGREDO
    
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
    
    # 2. Busca produtos relacionados
    cur.execute("""
        SELECT * FROM tb_produtos 
        WHERE categoria = ? AND id_produto != ? AND ativo = 1 
        ORDER BY RANDOM() LIMIT 4
    """, (produto['categoria'], id_produto))
    relacionados = cur.fetchall()
    
    # --- 3. NOVO: BUSCA OS FAVORITOS ---
    ids_favoritos = []
    if 'id_cliente' in session:
        user_id = session['id_cliente']
        cur.execute("SELECT id_produto FROM tb_favoritos WHERE id_cliente = ?", (user_id,))
        ids_favoritos = [item[0] for item in cur.fetchall()]
    # -----------------------------------

    con.close()
    
    # 4. Retorna enviando ids_favoritos
    return render_template("site/produto-detalhe.html", 
                           p=produto, 
                           relacionados=relacionados,
                           ids_favoritos=ids_favoritos) # <--- IMPORTANTE


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
    # Se já estiver logado:
    if 'id_cliente' in session:
        # Se veio com pedido de ir pro checkout, manda pra lá
        if request.args.get('redirect') == 'checkout':
            return redirect("/checkout")
        return redirect("/area_cliente/area-cliente.html")

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM tb_clientes WHERE email = ?", (email,))
        usuario = cur.fetchone()
        con.close()
        
        # Verifica se o usuário existe e se a senha bate
        if usuario and check_password_hash(usuario['senha'], senha):
            session['id_cliente'] = usuario['id_cliente']
            session['nome_cliente'] = usuario['nome'].split()[0]
            
            # --- CORREÇÃO AQUI: Verifica para onde ir ---
            if request.args.get('redirect') == 'checkout':
                return redirect("/checkout")
            # --------------------------------------------
            
            return redirect("/") # Se não tiver redirect, vai pra Home
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
    # 1. Pega a quantidade da URL (se não tiver, usa 1)
    qtd_selecionada = int(request.args.get('qtd', 1))

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_produtos WHERE id_produto = ?", (id_produto,))
    produto_db = cur.fetchone()
    con.close()
    
    if not produto_db:
        return "Produto não encontrado", 404

    preco = float(produto_db['preco_venda'])
    
    # 2. Cria o item já com a quantidade certa
    novo_item = {
        'id': produto_db['id_produto'],
        'nome': produto_db['nome_produto'],
        'preco': preco,
        'imagem': produto_db['img_produto'],
        'sku': produto_db['sku'],
        'qtd': qtd_selecionada,          # <--- USA A QTD QUE VEIO DA URL
        'subtotal': preco * qtd_selecionada # <--- CALCULA O SUBTOTAL CERTO
    }

    if 'carrinho' not in session:
        session['carrinho'] = []

    carrinho_atual = session['carrinho']
    encontrou = False

    for item in carrinho_atual:
        if item['id'] == id_produto:
            # Se já existe, soma a quantidade nova com a antiga
            item['qtd'] += qtd_selecionada
            item['subtotal'] = item['qtd'] * item['preco']
            encontrou = True
            break

    if not encontrou:
        carrinho_atual.append(novo_item)

    session['carrinho'] = carrinho_atual
    session.modified = True
    
    return redirect("/carrinho")
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
    # 1. Segurança: Se não tem carrinho, manda voltar
    if 'carrinho' not in session or not session['carrinho']:
        return redirect("/produtos")
    
    carrinho = session['carrinho']
    total_geral = sum(item['subtotal'] for item in carrinho)
    
    # 2. Dados do Cliente (Se estiver logado)
    cliente = None
    enderecos = []
    cartoes = [] # <--- 1. Cria a lista vazia para não dar erro se não tiver login
    
    if 'id_cliente' in session:
        con = get_db()
        cur = con.cursor()
        
        # Pega dados básicos
        cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (session['id_cliente'],))
        cliente = cur.fetchone()
        
        # Pega endereços extras
        cur.execute("SELECT * FROM tb_enderecos WHERE id_cliente = ?", (session['id_cliente'],))
        enderecos = cur.fetchall()

        # --- 2. BUSCA OS CARTÕES DO CLIENTE ---
        cur.execute("SELECT * FROM tb_cartoes WHERE id_cliente = ?", (session['id_cliente'],))
        cartoes = cur.fetchall()
        # --------------------------------------
        
        con.close()
    
    # 3. Renderiza passando tudo (INCLUINDO OS CARTÕES)
    return render_template("site/checkout.html", 
                           carrinho=carrinho, 
                           total_geral=total_geral,
                           cliente=cliente,       
                           enderecos=enderecos,
                           cartoes=cartoes)   # <--- 3. Envia a lista para o HTML

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    # 1. Verificações Básicas
    if 'id_cliente' not in session: return redirect("/login")
    if 'carrinho' not in session or not session['carrinho']: return redirect("/produtos")

    id_cliente = session['id_cliente']
    carrinho = session['carrinho']
    
    # Coleta dados
    forma_pagamento = request.form.get("forma_pagamento")
    cartao_selecionado = request.form.get("cartao_selecionado", "novo") # Pega a escolha (ID ou 'novo')
    qtd_parcelas = request.form.get("parcelas_escolhidas", 1)
    
    # Totais
    valor_total = sum(item['subtotal'] for item in carrinho)
    if forma_pagamento in ['pix', 'boleto']: valor_total *= 0.95

    con = get_db()
    cur = con.cursor()

    try:
        # 3. Lógica do Cartão (Novo ou Salvo)
        if forma_pagamento == 'credit':
            
            # Se escolheu digitar um NOVO cartão
            if cartao_selecionado == 'novo':
                numero_html = request.form.get("card_number_input", "")
                nome_html = request.form.get("card_holder_input", "")
                save_option = request.form.get("save_card_check") 

                # Validação simples (Só exige dados se for novo)
                if not numero_html or not nome_html:
                    return "Erro: Digite os dados do cartão."

                # Salvar Cartão se solicitado
                if save_option == 'sim':
                    try:
                        ultimos_4 = numero_html.replace(" ", "")[-4:]
                        token = f"tok_{int(datetime.now().timestamp())}"
                        validade = request.form.get("card_expiry_input", "")
                        bandeira = "Visa" if numero_html.startswith("4") else "Mastercard"
                        
                        cur.execute("""
                            INSERT INTO tb_cartoes (id_cliente, nome_titular, ultimos_4, bandeira, token_pagamento, validade) 
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (id_cliente, nome_html, ultimos_4, bandeira, token, validade))
                    except: pass # Se der erro ao salvar, não para a venda
            
            # Se escolheu um JÁ SALVO
            else:
                # Aqui você usaria o ID do cartão (cartao_selecionado) para processar no gateway
                print(f"Processando com cartão salvo ID: {cartao_selecionado}")

        # 4. Salvar Pedido
        status_inicial = 'Aguardando Pagamento' if forma_pagamento == 'boleto' else 'Pendente'
        
        cur.execute("""
            INSERT INTO tb_pedidos (id_cliente, data_pedido, status, valor_total, data_entrega, forma_pagamento, parcelas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_cliente, datetime.now(), status_inicial, valor_total, datetime.now(), forma_pagamento, qtd_parcelas))
        
        id_novo_pedido = cur.lastrowid 

        # 5. Salvar Itens e Financeiro
        for item in carrinho:
            cur.execute("INSERT INTO tb_itensPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)", 
                        (id_novo_pedido, item['id'], item['qtd'], item['preco'], item['subtotal']))

        cur.execute("INSERT INTO tb_contasReceber (descricao, valor, data_emissao, data_venc, categoria, status, id_pedido, id_cliente) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                    (f"Venda #{id_novo_pedido}", valor_total, datetime.now(), datetime.now(), "Venda Online", 'Recebido', id_novo_pedido, id_cliente))

        con.commit()
        session['carrinho'] = []
        session.modified = True
        
        return redirect(f"/compra-confirmada/{id_novo_pedido}")

    except Exception as e:
        con.rollback()
        print(f"Erro: {e}")
        return f"Erro: {e}"
    finally:
        con.close()

# --- NOVA ROTA: TELA DE SUCESSO ---
@app.route("/compra-confirmada/<int:id_pedido>")
def compra_confirmada(id_pedido):
    if 'id_cliente' not in session: return redirect("/login")
    
    con = get_db()
    cur = con.cursor()
    
    # Busca o pedido
    cur.execute("SELECT * FROM tb_pedidos WHERE id_pedido = ? AND id_cliente = ?", (id_pedido, session['id_cliente']))
    pedido = cur.fetchone()
    
    con.close()
    
    if not pedido:
        return redirect("/")
        
    return render_template("site/sucesso.html", pedido=pedido)
        
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

# --- 1. ROTA PARA EXIBIR A PÁGINA DE FAVORITOS ---
@app.route("/area_cliente/favoritos.html")
def pagina_favoritos():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    con = get_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Busca os dados do cliente para o menu lateral
    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (id_cliente,))
    cliente = cur.fetchone()

    # Busca os produtos favoritados
    cur.execute("""
        SELECT p.* FROM tb_produtos p
        JOIN tb_favoritos f ON p.id_produto = f.id_produto
        WHERE f.id_cliente = ?
    """, (id_cliente,))
    
    favoritos = cur.fetchall()
    con.close()
    
    # Envia para o HTML
    return render_template("area_cliente/favoritos.html", cliente=cliente, favoritos=favoritos, qtd_carrinho=len(session.get('carrinho', [])))


# --- 2. ROTA PARA ADICIONAR/REMOVER (Link direto) ---
@app.route("/favoritar/<int:id_produto>")
def acao_favoritar(id_produto):
    if 'id_cliente' not in session:
        return redirect("/login") # Manda pro login se não estiver logado
    
    id_cliente = session['id_cliente']
    con = get_db()
    cur = con.cursor()
    
    # Verifica se já existe
    cur.execute("SELECT * FROM tb_favoritos WHERE id_cliente = ? AND id_produto = ?", (id_cliente, id_produto))
    existe = cur.fetchone()
    
    if existe:
        # Se já tem, remove
        cur.execute("DELETE FROM tb_favoritos WHERE id_cliente = ? AND id_produto = ?", (id_cliente, id_produto))
    else:
        # Se não tem, adiciona
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        cur.execute("INSERT INTO tb_favoritos (id_cliente, id_produto, data_adicionado) VALUES (?, ?, ?)", (id_cliente, id_produto, data_hoje))
        
    con.commit()
    con.close()
    
    # Volta para a página anterior (seja produto ou lista de favoritos)
    return redirect(request.referrer or "/produtos")


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
# --- ROTA CORRIGIDA: ADICIONAR CARTÃO ---
# Removemos o "/area_cliente" do começo para bater com o action do HTML
@app.route("/adicionar_cartao", methods=['POST'])
def adicionar_cartao():
    if 'id_cliente' not in session: return redirect("/login")
    
    id_cliente = session['id_cliente']
    
    # Pega dados do Form HTML
    nome = request.form['nome_titular']
    numero_completo = request.form['numero_cartao']
    validade = request.form['validade']
    
    # 1. Pega apenas os últimos 4 dígitos
    # (Mudamos o nome da variável para não confundir)
    ultimos_4_db = numero_completo.replace(" ", "")[-4:]
    
    # 2. Identifica a bandeira
    bandeira = 'Visa' if numero_completo.startswith('4') else 'Mastercard'
    if numero_completo.startswith('3'): bandeira = 'Amex'
    
    # 3. Gera token (Obrigatório no seu banco)
    from datetime import datetime
    token_falso = f"tok_manual_{int(datetime.now().timestamp())}"
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # AQUI ESTAVA O ERRO DE BANCO:
        # Trocamos 'numero_final' por 'ultimos_4' e adicionamos 'token_pagamento'
        cur.execute("""
            INSERT INTO tb_cartoes 
            (id_cliente, nome_titular, ultimos_4, bandeira, validade, token_pagamento)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_cliente, nome, ultimos_4_db, bandeira, validade, token_falso))
        
        con.commit()
        print("✅ Cartão adicionado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao salvar cartão: {e}")
        con.rollback()
        
    finally:
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


@app.route("/area_cliente/pedido/<int:id_pedido>")
def detalhes_pedido(id_pedido):
    if 'id_cliente' not in session: return redirect("/login")
    
    con = get_db()
    cur = con.cursor()
    
    # 1. Busca o Pedido (E garante que pertence ao cliente logado para segurança)
    cur.execute("""
        SELECT * FROM tb_pedidos 
        WHERE id_pedido = ? AND id_cliente = ?
    """, (id_pedido, session['id_cliente']))
    pedido = cur.fetchone()
    
    # Se não achar o pedido (ou se for de outro cliente), volta pra lista
    if not pedido:
        con.close()
        return redirect("/area_cliente/meus-pedidos.html")
        
    # 2. Busca os Itens desse pedido (Juntando com a tabela de produtos para pegar nome e foto)
    cur.execute("""
        SELECT ip.*, p.nome_produto, p.sku, p.img_produto
        FROM tb_itensPedido ip
        JOIN tb_produtos p ON ip.id_produto = p.id_produto
        WHERE ip.id_pedido = ?
    """, (id_pedido,))
    itens = cur.fetchall()
    
    # 3. Busca dados do cliente para manter o menu lateral funcionando
    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente = ?", (session['id_cliente'],))
    cliente = cur.fetchone()
    
    con.close()
    
    return render_template("area_cliente/detalhes-pedido.html", 
                           pedido=pedido, 
                           itens=itens, 
                           cliente=cliente)

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