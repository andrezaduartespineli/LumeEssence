import sqlite3
from datetime import datetime

# Conecta ao banco de dados
con = sqlite3.connect("db_lume.db")
cur = con.cursor()

print("🔌 Conectado ao banco de dados...")

# Lista de Funcionários Fictícios
# Formato: (Nome, CPF, Data Nasc, Celular, Email Pessoal, Cargo, Depto, Email Login, Senha, Permissão)
equipe = [
    ('Ana Silva', '123.456.789-00', '15/03/1985', '(11) 99999-1111', 'ana.silva@email.com', 'Gerente Geral', 'Administrativo', 'admin@lume.com', '123456', 'Gerente'),
    ('Carlos Souza', '234.567.890-11', '20/06/1990', '(11) 98888-2222', 'carlos.souza@email.com', 'Assistente de Estoque', 'Produção/Estoque', 'estoque@lume.com', '123456', 'Estoquista'),
    ('Mariana Oliveira', '345.678.901-22', '10/11/1988', '(11) 97777-3333', 'mari.oli@email.com', 'Analista Financeiro', 'Financeiro', 'financeiro@lume.com', '123456', 'Financeiro'),
    ('Lucas Pereira', '456.789.012-33', '05/02/1995', '(11) 96666-4444', 'lucas.mkt@email.com', 'Social Media', 'Marketing', 'marketing@lume.com', '123456', 'Administrador'),
    ('Fernanda Costa', '567.890.123-44', '30/08/1982', '(11) 95555-5555', 'fernanda.jur@email.com', 'Consultora Jurídica', 'Jurídico', 'juridico@lume.com', '123456', 'Jurídico'),
    ('Roberto Alves', '678.901.234-55', '12/12/1992', '(11) 94444-6666', 'beto.vendas@email.com', 'Vendedor Sênior', 'Vendas', 'vendas@lume.com', '123456', 'Administrador')
]

try:
    for f in equipe:
        # Prepara dados padrão
        img_padrao = "sem_foto_user.png"
        ativo = 1 # 1 = Ativo, 0 = Inativo
        
        # SQL de Inserção
        cur.execute("""
            INSERT INTO tb_funcionarios 
            (nome, cpf, data_nasc, tel_cel, email_pessoal, cargo, departamento, email_login, senha, permissao, img_funcionario, ativo, data_cad) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], img_padrao, ativo))
        
        print(f"✅ Colaborador cadastrado: {f[0]} ({f[5]})")

    con.commit()
    print("\n🎉 Sucesso! Equipe cadastrada.")
    print("🔑 A senha padrão para todos é: 123456")

except Exception as e:
    print(f"\n❌ Erro ao inserir: {e}")
    con.rollback()

finally:
    con.close()