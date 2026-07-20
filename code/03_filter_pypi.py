import polars as pl
from pathlib import Path

DATASET_DIR = Path("../dataset")
PROCESSED_DIR = Path("../dataset_parquet")

def filter_pypi_dataset():
    """
    Filtra el dataset masivo de 24GB para extraer EXCLUSIVAMENTE los paquetes
    y dependencias de PyPI (Python). Esto reduce drásticamente el uso de memoria
    para los algoritmos de grafos del Capítulo 4.
    """
    print("Filtrando proyectos de PyPI...")
    
    # Filtrar projects.csv
    # Usamos scan_csv (lazy) para no saturar la memoria
    projects_csv = DATASET_DIR / "projects-1.6.0-2020-01-12.csv"
    pypi_projects_file = PROCESSED_DIR / "pypi_projects.parquet"
    
    if not pypi_projects_file.exists():
        (
            pl.scan_csv(projects_csv, ignore_errors=True, infer_schema_length=10000)
            .filter(pl.col("Platform") == "Pypi")
            .sink_parquet(pypi_projects_file)
        )
        print("Proyectos de PyPI guardados en pypi_projects.parquet")
    else:
        print("El archivo pypi_projects.parquet ya existe.")

    print("\nFiltrando dependencias de PyPI (solo runtime)...")
    
    # Filtrar dependencies.csv
    deps_csv = DATASET_DIR / "dependencies-1.6.0-2020-01-12.csv"
    pypi_deps_file = PROCESSED_DIR / "pypi_dependencies.parquet"
    
    if not pypi_deps_file.exists():
        (
            pl.scan_csv(deps_csv, ignore_errors=True, infer_schema_length=10000)
            .filter(
                (pl.col("Platform") == "Pypi") & 
                (pl.col("Dependency Kind") == "runtime")
            )
            .sink_parquet(pypi_deps_file)
        )
        print("Dependencias de PyPI guardadas en pypi_dependencies.parquet")
    else:
        print("El archivo pypi_dependencies.parquet ya existe.")

if __name__ == "__main__":
    PROCESSED_DIR.mkdir(exist_ok=True)
    filter_pypi_dataset()
    print("¡Filtrado completado! Ahora puedes ejecutar los scripts del Capítulo 4.")
