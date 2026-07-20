# Entorno de Procesamiento de Datos (AEDE - TIF)

Este directorio contiene el entorno y los scripts necesarios para procesar el dataset de Libraries.io (Open Source Repository and Dependency Metadata), el cual pesa aproximadamente 24GB.

Dado el tamaño del dataset, **no es posible cargarlo directamente en memoria (RAM) usando herramientas tradicionales como `pandas`**. En su lugar, hemos configurado un entorno que utiliza herramientas diseñadas para procesamiento "Out-of-Core" (fuera de la memoria) y computación "Lazy" (perezosa):

1. **Polars**: Un motor de DataFrames ultrarrápido escrito en Rust. Utiliza evaluación perezosa para leer y filtrar datos por lotes (streaming) sin cargar todo el archivo.
2. **DuckDB**: Un sistema de gestión de bases de datos analíticas SQL en proceso. Es extremadamente rápido y puede ejecutar consultas complejas directamente sobre archivos CSV o Parquet en el disco, consumiendo poca memoria RAM.
3. **Parquet**: Un formato de almacenamiento en columnas. Es altamente comprimido y permite a herramientas como Polars y DuckDB leer solo las columnas necesarias, acelerando drásticamente el análisis.

## Estructura de Scripts

- `requirements.txt`: Dependencias de Python necesarias.
- `01_convert_to_parquet.py`: Script inicial indispensable. Este script lee los archivos `.csv` enormes del directorio `../dataset` y los convierte a formato `.parquet` en `../dataset_parquet`. **Deberás ejecutar este script primero** una vez que tengas el dataset completo de 24GB. Tardará un rato en completarse la primera vez.
- `02_exploratory_analysis.py`: Un script de ejemplo que demuestra cómo realizar consultas (queries) muy rápidas y análisis exploratorio directamente sobre los archivos `.parquet` (o `.csv`) usando `DuckDB` y `Polars`.

## Cómo empezar

1. **Activar el entorno virtual** (ya fue creado y las dependencias instaladas):
   ```bash
   source .venv/bin/activate
   ```

2. **Ejecutar la conversión (Una vez que tengas el dataset completo)**:
   ```bash
   python 01_convert_to_parquet.py
   ```

3. **Ejecutar el análisis de prueba**:
   ```bash
   python 02_exploratory_analysis.py
   ```

## Análisis Interactivo (Jupyter)

También instalamos `jupyterlab` y `jupyter`. Puedes iniciar un entorno de notebooks (recomendado para análisis exploratorio y para hacer el TIF) con el siguiente comando:
```bash
jupyter lab
```

### Recomendaciones Generales para el Dataset de 24GB

* **Nunca uses `pd.read_csv()`** para los archivos completos, la memoria de tu computadora se agotará.
* Usa siempre **Polars (`pl.scan_parquet()`)** o **DuckDB (`duckdb.query()`)**.
* Si necesitas una parte de los datos en `pandas` (por ejemplo, para entrenar un modelo específico o usar una librería que solo soporta pandas), primero filtra y reduce los datos con Polars/DuckDB, y luego llama `.to_pandas()` o `.df()` sobre el resultado ya reducido (por ejemplo, las primeras 10,000 filas o datos agrupados).
