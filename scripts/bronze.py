import csv
import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "pipeline.db")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def criar_tabela_bronze_vendas(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bronze_vendas (
            id_venda TEXT,
            id_cliente TEXT,
            produto TEXT,
            quantidade TEXT,
            preco_unitario TEXT,
            data_venda TEXT,
            canal TEXT
        )
    """)


def criar_tabela_bronze_clientes(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bronze_clientes (
            id_cliente TEXT,
            nome TEXT,
            email TEXT,
            cidade TEXT,
            estado TEXT,
            data_cadastro TEXT
        )
    """)


def carregar_csv_para_bronze(conn, csv_path, tabela):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        placeholders = ", ".join(["?"] * len(headers))
        sql = f"INSERT INTO {tabela} VALUES ({placeholders})"
        for row in reader:
            conn.execute(sql, row)
    print(f"  [Bronze] {tabela}: dados carregados de {os.path.basename(csv_path)}")


def executar_bronze():
    print("=" * 50)
    print("CAMADA BRONZE - Ingestao de dados brutos")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    criar_tabela_bronze_vendas(conn)
    criar_tabela_bronze_clientes(conn)
    conn.execute("DELETE FROM bronze_vendas")
    conn.execute("DELETE FROM bronze_clientes")

    carregar_csv_para_bronze(conn, os.path.join(RAW_DIR, "vendas.csv"), "bronze_vendas")
    carregar_csv_para_bronze(conn, os.path.join(RAW_DIR, "clientes.csv"), "bronze_clientes")

    qtd_vendas = conn.execute("SELECT COUNT(*) FROM bronze_vendas").fetchone()[0]
    qtd_clientes = conn.execute("SELECT COUNT(*) FROM bronze_clientes").fetchone()[0]
    print(f"  [Bronze] bronze_vendas: {qtd_vendas} registros")
    print(f"  [Bronze] bronze_clientes: {qtd_clientes} registros")

    conn.commit()
    conn.close()
    print("  [Bronze] Concluida!\n")


if __name__ == "__main__":
    executar_bronze()
