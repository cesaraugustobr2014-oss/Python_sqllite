import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scripts.bronze import executar_bronze
from scripts.silver import executar_silver
from scripts.gold import executar_gold


def main():
    print("\n")
    print("*" * 50)
    print("  PIPELINE DE DADOS - ARQUITETURA MEDALHAO")
    print("  Python + SQLite")
    print("*" * 50)
    print()

    db_path = os.path.join(os.path.dirname(__file__), "database", "pipeline.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    executar_bronze()
    executar_silver()
    executar_gold()

    print("=" * 50)
    print("  PIPELINE CONCLUIDO COM SUCESSO!")
    print("=" * 50)
    print(f"  Banco de dados: {os.path.abspath(db_path)}")
    print()


if __name__ == "__main__":
    main()
