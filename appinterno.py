from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Função auxiliar para conectar
def get_db():
    return sqlite3.connect("db_lume.db")

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
    cur.execute("SELECT * FROM tb_clientes")
    dados = cur.fetchall()
    con.close()
    return render_template("cliente.html", clientes=dados)

@app.route("/cliente/novo", methods=["GET", "POST"])
def cliente_novo():
    if request.method == "POST":
        nome = request.form["nome"]
        data_nasc = request.form["data_nasc"]
        tel = request.form["tel"]
        email = request.form["email"]

        con = get_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO tb_clientes (nome, data_nasc, tel_cel, email)
            VALUES (?, ?, ?, ?)
        """, (nome, data_nasc, tel, email))
        con.commit()
        con.close()
        return redirect("/cliente")

    return render_template("form_cliente.html")

@app.route("/cliente/editar/<int:id>", methods=["GET", "POST"])
def cliente_editar(id):
    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        data_nasc = request.form["data_nasc"]
        tel = request.form["tel"]
        email = request.form["email"]

        cur.execute("""
            UPDATE tb_clientes
            SET nome=?, data_nasc=?, tel_cel=?, email=?
            WHERE id_clientes=?
        """, (nome, data_nasc, tel, email, id))

        con.commit()
        con.close()
        return redirect("/cliente")

    cur.execute("SELECT * FROM tb_clientes WHERE id_clientes=?", (id,))
    cliente = cur.fetchone()
    con.close()

    return render_template("form_cliente.html", cliente=cliente)

@app.route("/cliente/delete/<int:id>")
def cliente_delete(id):
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM tb_clientes WHERE id_clientes=?", (id,))
    con.commit()
    con.close()
    return redirect("/cliente")
#

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
        razao_social = request.form["razao_social"]
        nome_fantasia = request.form["nome_fantasia"]
        cnpj = request.form["cnpj"]
        tel_cel = request.form["tel_cel"]
        categoria = request.form["categoria"]
        insc_estadual = request.form["insc_estadual"]
        email = request.form["email"]
        cep = request.form["cep"]
        endereco = request.form["endereco"]
        cidade = request.form["cidade"]
        estado = request.form["estado"]
        data_cad = request.form["data_cad"]


        con = get_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO tb_fornecedores (razao_social, nome_fantasia, cnpj, tel_cel, categoria, insc_estadual, email, cep, endereco, cidade, estado, data_cad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (razao_social, nome_fantasia, cnpj, tel_cel, categoria, insc_estadual, email, cep, endereco, cidade, estado, data_cad))
        con.commit()
        con.close()
        return redirect("/fornecedores")

    return render_template("novo-fornecedor.html")

@app.route("/fornecedor/editar/<int:id>", methods=["GET", "POST"])
def fornecedor_editar(id):
    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]

        cur.execute("""
            UPDATE tb_fornecedores
            SET nome=?, email=?
            WHERE id=?
        """, (nome, email, id))

        con.commit()
        con.close()
        return redirect("/fornecedor")

    cur.execute("SELECT * FROM tb_fornecedores WHERE id=?", (id,))
    fornecedor = cur.fetchone()
    con.close()

    return render_template("form_fornecedor.html", fornecedor=fornecedor)

@app.route("/fornecedor/delete/<int:id>")
def fornecedor_delete(id):
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM tb_fornecedores WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/fornecedor")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
