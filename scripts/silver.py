import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "pipeline.db")


def criar_tabelas_silver(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS silver_vendas (
            id_venda INTEGER PRIMARY KEY,
            id_cliente INTEGER,
            produto TEXT,
            quantidade INTEGER,
            preco_unitario REAL,
            valor_total REAL,
            data_venda DATE,
            canal TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS silver_clientes (
            id_cliente INTEGER PRIMARY KEY,
            nome TEXT,
            email TEXT,
            cidade TEXT,
            estado TEXT,
            data_cadastro DATE
        )
    """)


def validar_data(data_str):
    try:
        datetime.strptime(data_str.strip(), "%Y-%m-%d")
        return True
    except (ValueError, AttributeError):
        return False


def processar_vendas(conn):
    conn.execute("DELETE FROM silver_vendas")

    rows = conn.execute("SELECT * FROM bronze_vendas").fetchall()
    inseridos = 0
    duplicados = 0
    invalidos = 0

    vendas_validas = {}
    for row in rows:
        id_venda, id_cliente, produto, quantidade, preco_unitario, data_venda, canal = row

        if id_venda in vendas_validas:
            duplicados += 1
            continue

        if not id_cliente or not id_cliente.strip():
            invalidos += 1
            continue

        if not data_venda or not validar_data(data_venda):
            invalidos += 1
            continue

        try:
            qtd = int(quantidade) if quantidade and quantidade.strip() else None
            preco = float(preco_unitario) if preco_unitario and preco_unitario.strip() else None
        except (ValueError, TypeError):
            invalidos += 1
            continue

        if qtd is None or preco is None or qtd <= 0:
            invalidos += 1
            continue

        canal_limpo = canal.strip().lower() if canal and canal.strip() else "nao_informado"
        valor_total = round(qtd * preco, 2)

        vendas_validas[id_venda] = (
            int(id_venda),
            int(id_cliente),
            produto.strip(),
            qtd,
            preco,
            valor_total,
            data_venda.strip(),
            canal_limpo,
        )

    for venda in vendas_validas.values():
        conn.execute(
            "INSERT INTO silver_vendas VALUES (?, ?, ?, ?, ?, ?, ?, ?)", venda
        )
        inseridos += 1

    print(f"  [Silver] silver_vendas: {inseridos} validos, {duplicados} duplicados, {invalidos} invalidos")


def processar_clientes(conn):
    conn.execute("DELETE FROM silver_clientes")

    rows = conn.execute("SELECT * FROM bronze_clientes").fetchall()
    inseridos = 0
    duplicados = 0
    invalidos = 0

    clientes_validos = {}
    for row in rows:
        id_cliente, nome, email, cidade, estado, data_cadastro = row

        if id_cliente in clientes_validos:
            duplicados += 1
            continue

        if not nome or not nome.strip():
            invalidos += 1
            continue

        if not estado or not estado.strip():
            invalidos += 1
            continue

        email_limpo = email.strip() if email and email.strip() else None
        cidade_limpa = cidade.strip() if cidade and cidade.strip() else None

        clientes_validos[id_cliente] = (
            int(id_cliente),
            nome.strip(),
            email_limpo,
            cidade_limpa,
            estado.strip().upper(),
            data_cadastro.strip() if data_cadastro else None,
        )

    for cliente in clientes_validos.values():
        conn.execute(
            "INSERT INTO silver_clientes VALUES (?, ?, ?, ?, ?, ?)", cliente
        )
        inseridos += 1

    print(f"  [Silver] silver_clientes: {inseridos} validos, {duplicados} duplicados, {invalidos} invalidos")


def executar_silver():
    print("=" * 50)
    print("CAMADA SILVER - Limpeza e transformacao")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    criar_tabelas_silver(conn)
    processar_vendas(conn)
    processar_clientes(conn)

    qtd_vendas = conn.execute("SELECT COUNT(*) FROM silver_vendas").fetchone()[0]
    qtd_clientes = conn.execute("SELECT COUNT(*) FROM silver_clientes").fetchone()[0]
    print(f"  [Silver] Total silver_vendas: {qtd_vendas}")
    print(f"  [Silver] Total silver_clientes: {qtd_clientes}")

    conn.commit()
    conn.close()
    print("  [Silver] Concluida!\n")


if __name__ == "__main__":
    executar_silver()
