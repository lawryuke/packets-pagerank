import duckdb
import polars as pl
from pathlib import Path

PROCESSED_DIR = Path("../dataset_parquet")
DATASET_DIR = Path("../dataset")

def query_with_duckdb():
    print("--- Consultas con DuckDB ---")
    con = duckdb.connect()
    
    # Ejemplo de consulta: contar filas totales en un archivo
    try:
        # Intenta consultar el archivo parquet (muy rápido)
        parquet_file = PROCESSED_DIR / "projects_with_repository_fields-1.6.0-2020-01-12.parquet"
        if parquet_file.exists():
            print(f"Consultando {parquet_file.name}...")
            result = con.execute(f"SELECT count(*) FROM '{parquet_file}'").fetchone()
            print(f"Total de proyectos (Parquet): {result[0]}")
        else:
            # Si no existe, intenta con el CSV directamente (DuckDB puede leer CSV, pero tarda más)
            csv_file = DATASET_DIR / "projects_with_repository_fields-1.6.0-2020-01-12.csv"
            print(f"Parquet no encontrado. Consultando CSV: {csv_file.name}...")
            result = con.execute(f"SELECT count(*) FROM read_csv_auto('{csv_file}')").fetchone()
            print(f"Total de proyectos (CSV): {result[0]}")
            
    except Exception as e:
        print(f"Error consultando DuckDB: {e}")

def query_with_polars():
    print("\n--- Consultas con Polars ---")
    try:
        parquet_file = PROCESSED_DIR / "projects_with_repository_fields-1.6.0-2020-01-12.parquet"
        if not parquet_file.exists():
            print(f"El archivo {parquet_file.name} no existe. Ejecuta primero 01_convert_to_parquet.py")
            return
            
        # scan_parquet crea un plan de ejecución perezoso (LazyFrame)
        df = pl.scan_parquet(parquet_file)
        
        # Ejemplo: Contar proyectos por Lenguaje
        # La evaluación solo ocurre al llamar a .collect()
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
    print("Ejemplos de análisis exploratorio (EDA) de datos masivos out-of-core.")
    query_with_duckdb()
    query_with_polars()
