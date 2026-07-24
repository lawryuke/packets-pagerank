"""
Exploratory analysis module for massive out-of-core datasets using DuckDB and Polars.
"""
import duckdb
import polars as pl
from pathlib import Path

PROCESSED_DIR = Path("../dataset_parquet")
DATASET_DIR = Path("../dataset")

def query_with_duckdb():
    """Executes a sample query using DuckDB."""
    print("--- Consultas con DuckDB ---")
    con = duckdb.connect()
    try:
        parquet_file = PROCESSED_DIR / "projects_with_repository_fields-1.6.0-2020-01-12.parquet"
        if parquet_file.exists():
            print(f"Consultando {parquet_file.name}...")
            result = con.execute(f"SELECT count(*) FROM '{parquet_file}'").fetchone()
            print(f"Total de proyectos (Parquet): {result[0]}")
        else:
            csv_file = DATASET_DIR / "projects_with_repository_fields-1.6.0-2020-01-12.csv"
            print(f"Parquet no encontrado. Consultando CSV: {csv_file.name}...")
            result = con.execute(f"SELECT count(*) FROM read_csv_auto('{csv_file}')").fetchone()
            print(f"Total de proyectos (CSV): {result[0]}")
    except Exception as e:
        print(f"Error consultando DuckDB: {e}")

def query_with_polars():
    """Executes a sample query using Polars lazy evaluation."""
    print("\n--- Consultas con Polars ---")
    try:
        parquet_file = PROCESSED_DIR / "projects_with_repository_fields-1.6.0-2020-01-12.parquet"
        if not parquet_file.exists():
            print(f"El archivo {parquet_file.name} no existe. Ejecuta primero 01_convert_to_parquet.py")
            return
            
        df = pl.scan_parquet(parquet_file)
        lang_counts = (
            df
            .group_by('Language')
            .agg(pl.len().alias('count'))
            .sort('count', descending=True)
            .limit(10)
            .collect()
        )
        print("Top 10 Lenguajes de Programación:")
        print(lang_counts)
    except Exception as e:
        print(f"Error consultando Polars: {e}")

if __name__ == "__main__":
    query_with_duckdb()
    query_with_polars()
