from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime # Necessário para registrar a data e hora

app = Flask(__name__)

# Função auxiliar para conectar
def get_db():
    conn = sqlite3.connect("db_lume.db")
    # Isso permite acessar as colunas pelo nome (ex: cliente['nome'])
    conn.row_factory = sqlite3.Row 
    return conn

# -------------------------------
# Página Inicial
# -------------------------------
@app.route("/")
def index():
    return render_template("dashboard.html")

# -------------------------------
# CLIENTES
# -------------------------------
@app.route("/cliente")
def cliente():
    con = get_db()
    cur = con.cursor()
    # Pega todos os clientes
    cur.execute("SELECT * FROM tb_clientes")
    dados = cur.fetchall()
    con.close()
    return render_template("cliente.html", clientes=dados)

@app.route("/cliente/novo", methods=["GET", "POST"])
def cliente_novo():
    if request.method == "POST":
        nome = request.form["nome"]
        data_nasc = request.form["data_nasc"]
        cpf = request.form["cpf"]
        genero = request.form["genero"]
        tel_cel = request.form["tel_cel"] 
        email = request.form["email"]
        cep = request.form["cep"]
        endereco = request.form["endereco"]
        n = request.form["n"]
        complemento = request.form["complemento"]
        referencia = request.form["referencia"]
        bairro = request.form["bairro"]
        cidade = request.form["cidade"]
        estado = request.form["estado"]
                                
        # 2. Gera dados automáticos (Obrigatórios no banco, mas não pedidos no form)
        data_cad = datetime.now()
        

        con = get_db()
        cur = con.cursor()
        
        # 3. Insere TODOS os campos obrigatórios da tabela tb_clientes
        cur.execute("""
            INSERT INTO tb_clientes (
                nome, data_nasc, cpf, genero, tel_cel, email, 
                cep, endereco, n, complemento,referencia, bairro, cidade, estado, data_cad
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, data_nasc, cpf, genero, tel_cel, email, 
                cep, endereco, n, complemento,referencia, bairro, cidade, estado, data_cad))
        
        con.commit()
        con.close()
        return redirect("/cliente")

    return render_template("novo-cliente.html") # Verifique se o nome do arquivo HTML é esse

@app.route("/cliente/editar/<int:id>", methods=["GET", "POST"])
def cliente_editar(id):
    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        data_nasc = request.form["data_nasc"]
        tel_cel = request.form["tel_cel"]
        cep = request.form["cep"]
        endereco = request.form["endereco"]
        n = request.form["n"]
        complemento = request.form["complemento"]
        referencia = request.form["referencia"]
        bairro = request.form["bairro"]
        cidade = request.form["cidade"]
        estado = request.form["estado"]
        # Adicione outros campos se quiser permitir editar CPF/Data aqui

        cur.execute("""
            UPDATE tb_clientes
            SET nome=?, data_nasc=?, tel_cel=?, cep=?, endereco=?, n=?, complemento=?, referencia=?, bairro=?, cidade=?, estado=?
            WHERE id_cliente=? 
        """, (nome, data_nasc, tel_cel, cep, endereco, n, complemento, referencia, bairro, cidade, estado, id)) # Atenção: no seu banco a chave é id_cliente

        con.commit()
        con.close()
        return redirect("/cliente")

    cur.execute("SELECT * FROM tb_clientes WHERE id_cliente=?", (id,))
    cliente = cur.fetchone()
    con.close()

    return render_template("editar-cliente.html", cliente=cliente)

@app.route("/cliente/delete/<int:id>")
def cliente_delete(id):
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM tb_clientes WHERE id_cliente=?", (id,))
    con.commit()
    con.close()
    return redirect("/cliente")

# -------------------------------
# FORNECEDORES
# -------------------------------
@app.route("/fornecedores")
def fornecedor():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tb_fornecedores")
    dados = cur.fetchall()
    con.close()
    return render_template("fornecedores.html", fornecedores=dados)

@app.route("/novo-fornecedor", methods=["GET", "POST"])
def fornecedor_novo():
    if request.method == "POST":
        # Recebendo dados do formulário
        razao_social = request.form["razao_social"]
        nome_fantasia = request.form["nome_fantasia"]
        cnpj = request.form["cnpj"]
        tel_cel = request.form["tel_cel"]
        categoria = request.form["categoria"]
        insc_estadual = request.form.get("insc_estadual", "Isento") # .get evita erro se estiver vazio
        email = request.form["email"]
        cep = request.form["cep"]
        endereco = request.form["endereco"]
        cidade = request.form["cidade"]
        estado = request.form["estado"]
        
        # Data automática
        data_cad = datetime.now()

        con = get_db()
        cur = con.cursor()
        
        # Corrigido: Agora tem 12 interrogações para 12 campos
        cur.execute("""
            INSERT INTO tb_fornecedores (
                razao_social, nome_fantasia, cnpj, tel_cel, categoria, 
                insc_estadual, email, cep, endereco, cidade, estado, data_cad
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            razao_social, nome_fantasia, cnpj, tel_cel, categoria, 
            insc_estadual, email, cep, endereco, cidade, estado, data_cad
        ))
        
        con.commit()
        con.close()
        return redirect("/fornecedores")

    return render_template("novo-fornecedor.html")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)