"""
Module to filter PyPI projects and dependencies from the main dataset.
"""
import polars as pl
from pathlib import Path

DATASET_DIR = Path("../dataset")
PROCESSED_DIR = Path("../dataset_parquet")

def filter_pypi_dataset():
    """Filters the massive dataset to extract only PyPI packages and runtime dependencies."""
    print("Filtrando proyectos de PyPI...")
    
    projects_csv = DATASET_DIR / "projects_with_repository_fields-1.6.0-2020-01-12.csv"
    pypi_projects_file = PROCESSED_DIR / "pypi_projects.parquet"
    
    if not pypi_projects_file.exists():
        (
            pl.scan_csv(projects_csv, ignore_errors=True, infer_schema_length=10000, truncate_ragged_lines=True)
            .filter(pl.col("Platform").is_in(["Pypi", "pypi", "PyPI"]))
            .sink_parquet(pypi_projects_file)
        )
        print("Proyectos de PyPI guardados en pypi_projects.parquet")
    else:
        print("El archivo pypi_projects.parquet ya existe.")

    print("\nFiltrando dependencias de PyPI (solo runtime)...")
    
    deps_csv = DATASET_DIR / "repository_dependencies-1.6.0-2020-01-12.csv"
    pypi_deps_file = PROCESSED_DIR / "pypi_dependencies.parquet"
    
    if not pypi_deps_file.exists():
        (
            pl.scan_csv(deps_csv, ignore_errors=True, infer_schema_length=10000, truncate_ragged_lines=True)
            .filter(
                (pl.col("Manifest Platform").is_in(["Pypi", "pypi", "PyPI"])) & 
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
