import polars as pl
import os
from pathlib import Path

# Configurar rutas
DATASET_DIR = Path("../dataset")
PROCESSED_DIR = Path("../dataset_parquet")

def convert_csv_to_parquet(csv_file: Path, parquet_file: Path):
    print(f"Convirtiendo {csv_file.name} a {parquet_file.name}...")
    
    # scan_csv permite leer los datos de forma "lazy" (perezosa)
    # Esto evita cargar todo el archivo en la memoria RAM.
    # sink_parquet procesa y escribe el resultado por lotes (streaming)
    try:
        (
            pl.scan_csv(csv_file, ignore_errors=True, infer_schema_length=10000)
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
    
    # Procesar todos los archivos CSV en el directorio del dataset
    for csv_file in DATASET_DIR.glob("*.csv"):
        parquet_file = PROCESSED_DIR / f"{csv_file.stem}.parquet"
        
        # Si el archivo parquet no existe, lo convertimos
        if not parquet_file.exists():
            convert_csv_to_parquet(csv_file, parquet_file)
        else:
            print(f"Omitiendo {csv_file.name}, el archivo parquet ya existe.")

if __name__ == "__main__":
    print("Iniciando conversión de CSV a Parquet...")
    print("Nota: Para un dataset de 24GB, esto puede tomar un tiempo considerable.")
    main()
