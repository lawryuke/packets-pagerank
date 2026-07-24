# 💻 Código y Scripts de Análisis

Esta sección aloja el pipeline de procesamiento de datos, desde la conversión del dataset crudo hasta el análisis avanzado en grafos y visualización interactiva.

## ⚙️ Arquitectura Out-of-Core

Se evitan librerías tradicionales en memoria como `pandas` para cargas iniciales. En su lugar, implementamos **Polars** y **DuckDB** sobre archivos **Parquet**.

## 🚀 Guía Rápida de Ejecución

Sigue el orden de los scripts (01 a 07) para completar el análisis.

### 1. Transformación ETL
```bash
python 01_convert_to_parquet.py
python 02_exploratory_analysis.py
python 03_filter_pypi.py
```

### 2. Análisis Topológico y PageRank
```bash
python 04_graph_analysis.py
```
> **Nota:** Este proceso generará el archivo `pagerank_results.csv` tras aplicar los modelos de PageRank y partición de comunidades de Louvain.

### 3. Visualizaciones
```bash
python 05_visualize_graph.py
python 06_visualize_project_tree.py  # Genera HTML interactivo
python 07_cluster_analysis.py
python generate_wave_plot.py
```

## 📓 Modo Interactivo
Para experimentación y ejecución dinámica de consultas analíticas:
```bash
jupyter lab
```
*Se recomienda usar DuckDB y Polars para el sub-muestreo inicial antes de convertir a Pandas DataFrames en los notebooks.*
