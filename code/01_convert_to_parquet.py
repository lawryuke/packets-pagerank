"""
Script to convert massive CSV dataset files to Parquet format.
"""
import polars as pl
from pathlib import Path

DATASET_DIR = Path("../dataset")
PROCESSED_DIR = Path("../dataset_parquet")

def convert_csv_to_parquet(csv_file: Path, parquet_file: Path):
    """Converts a CSV file to Parquet using lazy evaluation and streaming."""
    print(f"Convirtiendo {csv_file.name} a {parquet_file.name}...")
    try:
        (
            pl.scan_csv(csv_file, ignore_errors=True, infer_schema_length=10000, truncate_ragged_lines=True)
            .sink_parquet(parquet_file)
        )
        print(f"Finalizado {parquet_file.name}")
    except Exception as e:
        print(f"Error al convertir {csv_file.name}: {e}")

def main():
    if not DATASET_DIR.exists():
        print(f"No se encontró el directorio del dataset: {DATASET_DIR}")
        return

    PROCESSED_DIR.mkdir(exist_ok=True)
    
    necessary_files = [
        "projects_with_repository_fields-1.6.0-2020-01-12.csv",
        "repository_dependencies-1.6.0-2020-01-12.csv"
    ]
    
    for filename in necessary_files:
        csv_file = DATASET_DIR / filename
        if not csv_file.exists():
            print(f"Advertencia: No se encontró el archivo {filename}")
            continue
            
        parquet_file = PROCESSED_DIR / f"{csv_file.stem}.parquet"
        
        if not parquet_file.exists():
            convert_csv_to_parquet(csv_file, parquet_file)
        else:
            print(f"Omitiendo {csv_file.name}, el archivo parquet ya existe.")

if __name__ == "__main__":
    main()
