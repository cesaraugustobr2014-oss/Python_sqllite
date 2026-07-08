import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "pipeline.db")


def criar_tabelas_gold(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gold_vendas_por_cliente (
            id_cliente INTEGER,
            nome TEXT,
            estado TEXT,
            total_compras INTEGER,
            total_gasto REAL,
            ticket_medio REAL,
            produto_favorito TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gold_ranking_produtos (
            posicao INTEGER,
            produto TEXT,
            total_vendido INTEGER,
            receita_total REAL,
            qtd_pedidos INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gold_vendas_por_estado (
            estado TEXT,
            total_vendas INTEGER,
            receita_total REAL,
            ticket_medio REAL,
            mes_referencia TEXT
        )
    """)


def gerar_vendas_por_cliente(conn):
    conn.execute("DELETE FROM gold_vendas_por_cliente")

    conn.execute("""
        INSERT INTO gold_vendas_por_cliente
        SELECT
            c.id_cliente,
            c.nome,
            c.estado,
            COUNT(v.id_venda) AS total_compras,
            ROUND(SUM(v.valor_total), 2) AS total_gasto,
            ROUND(AVG(v.valor_total), 2) AS ticket_medio,
            (
                SELECT v2.produto
                FROM silver_vendas v2
                WHERE v2.id_cliente = c.id_cliente
                GROUP BY v2.produto
                ORDER BY SUM(v2.quantidade) DESC
                LIMIT 1
            ) AS produto_favorito
        FROM silver_clientes c
        LEFT JOIN silver_vendas v ON c.id_cliente = v.id_cliente
        GROUP BY c.id_cliente
        ORDER BY total_gasto DESC
    """)

    print("  [Gold] gold_vendas_por_cliente: gerada")


def gerar_ranking_produtos(conn):
    conn.execute("DELETE FROM gold_ranking_produtos")

    conn.execute("""
        INSERT INTO gold_ranking_produtos
        SELECT
            ROW_NUMBER() OVER (ORDER BY SUM(quantidade) DESC) AS posicao,
            produto,
            SUM(quantidade) AS total_vendido,
            ROUND(SUM(valor_total), 2) AS receita_total,
            COUNT(*) AS qtd_pedidos
        FROM silver_vendas
        GROUP BY produto
        ORDER BY receita_total DESC
    """)

    print("  [Gold] gold_ranking_produtos: gerada")


def gerar_vendas_por_estado(conn):
    conn.execute("DELETE FROM gold_vendas_por_estado")

    conn.execute("""
        INSERT INTO gold_vendas_por_estado
        SELECT
            c.estado,
            COUNT(v.id_venda) AS total_vendas,
            ROUND(SUM(v.valor_total), 2) AS receita_total,
            ROUND(AVG(v.valor_total), 2) AS ticket_medio,
            STRFTIME('%Y-%m', v.data_venda) AS mes_referencia
        FROM silver_vendas v
        JOIN silver_clientes c ON v.id_cliente = c.id_cliente
        GROUP BY c.estado, STRFTIME('%Y-%m', v.data_venda)
        ORDER BY receita_total DESC
    """)

    print("  [Gold] gold_vendas_por_estado: gerada")


def exibir_resultados(conn):
    print("\n" + "-" * 60)
    print("RESULTADOS - Top 5 Clientes por Gasto")
    print("-" * 60)
    rows = conn.execute("SELECT * FROM gold_vendas_por_cliente LIMIT 5").fetchall()
    print(f"  {'ID':<5} {'Nome':<20} {'UF':<4} {'Compras':<8} {'Total Gasto':<12} {'Ticket Medio':<12}")
    for r in rows:
        print(f"  {r[0]:<5} {r[1]:<20} {r[2]:<4} {r[3]:<8} R$ {r[4]:<10.2f} R$ {r[5]:<10.2f}")

    print("\n" + "-" * 60)
    print("RESULTADOS - Ranking de Produtos")
    print("-" * 60)
    rows = conn.execute("SELECT * FROM gold_ranking_produtos").fetchall()
    print(f"  {'#':<3} {'Produto':<22} {'Qtd Vendida':<12} {'Receita':<14} {'Pedidos':<8}")
    for r in rows:
        print(f"  {r[0]:<3} {r[1]:<22} {r[2]:<12} R$ {r[3]:<12.2f} {r[4]:<8}")

    print("\n" + "-" * 60)
    print("RESULTADOS - Vendas por Estado/Mes")
    print("-" * 60)
    rows = conn.execute("SELECT * FROM gold_vendas_por_estado LIMIT 10").fetchall()
    print(f"  {'UF':<4} {'Mes':<10} {'Vendas':<8} {'Receita':<14} {'Ticket Medio':<12}")
    for r in rows:
        print(f"  {r[0]:<4} {r[4]:<10} {r[1]:<8} R$ {r[2]:<12.2f} R$ {r[3]:<10.2f}")


def executar_gold():
    print("=" * 50)
    print("CAMADA GOLD - Agregacoes de negocio")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    criar_tabelas_gold(conn)
    gerar_vendas_por_cliente(conn)
    gerar_ranking_produtos(conn)
    gerar_vendas_por_estado(conn)

    exibir_resultados(conn)

    conn.commit()
    conn.close()
    print("\n  [Gold] Concluida!\n")


if __name__ == "__main__":
    executar_gold()
