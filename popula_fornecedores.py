import sqlite3
from datetime import datetime

# Conecta ao banco de dados
con = sqlite3.connect("db_lume.db")
cur = con.cursor()

print("🔌 Conectado ao banco de dados...")

# Lista de Fornecedores Fictícios para Inserir
fornecedores = [
    ('Essências do Vale Ltda', 'Vale das Essências', '12.345.678/0001-90', '(11) 98765-4321', 'Matéria-prima', '123.456.789.000', 'contato@valeessencias.com.br', '01001-000', 'Av. das Flores, 123, Galpão 4', 'São Paulo', 'SP', 'Carlos Eduardo', 'Fornecedor principal de óleos essenciais e fragrâncias.'),
    
    ('Vidros & Potes Indústria e Comércio', 'Casa do Vidro', '98.765.432/0001-12', '(41) 99999-8888', 'Embalagens', '987.654.321.111', 'vendas@casadovidro.com.br', '80000-000', 'Rua do Vidraceiro, 500', 'Curitiba', 'PR', 'Fernanda Souza', 'Potes de vidro âmbar e tampas de madeira.'),
    
    ('Parafinas Nacionais S.A.', 'Parafina Brasil', '11.222.333/0001-44', '(21) 97777-6666', 'Matéria-prima', '111.222.333.444', 'comercial@parafinabrasil.com.br', '20000-000', 'Rodovia do Sol, Km 45', 'Rio de Janeiro', 'RJ', 'Roberto Lima', 'Cera de soja, cera de coco e pavios de algodão.'),
    
    ('Logística Rápida Express', 'Flash Entregas', '55.666.777/0001-88', '(31) 95555-4444', 'Logística', '555.666.777.888', 'sac@flashentregas.com.br', '30000-000', 'Via Expressa, 1000', 'Belo Horizonte', 'MG', 'Juliana Alves', 'Transportadora parceira para envios estaduais.'),
    
    ('Gráfica Criativa Ltda', 'PrintiArt', '44.555.666/0001-99', '(11) 93333-2222', 'Serviços', '444.555.666.999', 'arte@printiart.com.br', '04000-000', 'Rua da Impressão, 88', 'São Paulo', 'SP', 'Mariana Costa', 'Impressão de rótulos adesivos e tags personalizadas.'),
    
    ('Embalagens Ecológicas Ltda', 'EcoPack', '77.888.999/0001-00', '(51) 91111-2222', 'Embalagens', '777.888.999.000', 'contato@ecopack.com.br', '90000-000', 'Av. Verde, 200', 'Porto Alegre', 'RS', 'Lucas Mendes', 'Caixas de papelão reciclado e fitas biodegradáveis.'),
    
    ('Importadora Oriental', 'China Scents', '22.333.444/0001-55', '(11) 94444-5555', 'Matéria-prima', '222.333.444.555', 'import@chinascents.com', '03000-000', 'Rua 25 de Março, 500, Sala 12', 'São Paulo', 'SP', 'Li Wei', 'Essências importadas e moldes de silicone.')
]

try:
    for f in fornecedores:
        # Prepara a data de hoje
        hoje = datetime.now().strftime("%Y-%m-%d")
        
        # SQL de Inserção
        cur.execute("""
            INSERT INTO tb_fornecedores 
            (razao_social, nome_fantasia, cnpj, tel_cel, categoria, insc_estadual, email, cep, endereco, cidade, estado, nome_repre, observacao, data_cad) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[12], hoje))
        
        print(f"✅ Inserido: {f[1]}")

    con.commit()
    print("\n🎉 Sucesso! Todos os fornecedores foram cadastrados.")

except Exception as e:
    print(f"\n❌ Erro ao inserir: {e}")
    con.rollback()

finally:
    con.close()