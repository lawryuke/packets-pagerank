# 📦 Packets PageRank (AEDE - TIF)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Polars](https://img.shields.io/badge/Polars-Fast-orange.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-yellow.svg)
![NetworkX](https://img.shields.io/badge/NetworkX-Graphs-lightgrey.svg)

> **Evaluación del riesgo sistémico en ecosistemas de software de código abierto utilizando PageRank y análisis de grafos en grandes volúmenes de datos.**

Este proyecto procesa el dataset masivo de **Libraries.io** (~24GB) implementando herramientas "Out-of-Core" y "Lazy Computation" para calcular la centralidad y fragilidad de los paquetes del ecosistema PyPI.

## 🚀 Características Principales
- **Procesamiento Masivo:** Utilización de Polars y DuckDB para consultas analíticas de ultra alto rendimiento en memoria limitada.
- **Análisis Topológico:** Aplicación de teoría de grafos y algoritmos de comunidades (Louvain) mediante NetworkX.
- **PageRank Sistémico:** Adaptación del algoritmo de Google para cuantificar el impacto transitivo de vulnerabilidades de software.
- **Visualización Interactiva:** Generación de redes de dependencias locales y diagramas jerárquicos de propagación con PyVis y Matplotlib.

## 📂 Estructura del Proyecto
- `dataset/`: Archivos CSV originales (no incluidos, descargar de Libraries.io).
- `dataset_parquet/`: Datos convertidos y comprimidos (generados mediante los scripts).
- `code/`: Código fuente en Python para ETL y análisis algorítmico.

## 🛠 Instalación y Configuración

1. **Clonar el repositorio e instalar dependencias:**
   ```bash
   git clone https://github.com/tu-usuario/packets-pagerank.git
   cd packets-pagerank/code
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Flujo de Ejecución:**
   Visite la carpeta [`code`](./code/README.md) para ejecutar paso a paso la tubería de análisis de datos.

## 📊 Resultados Visuales

El proyecto genera visualizaciones clave para entender el ecosistema de Python:
- **Red de Impacto Local**: Subgrafos y ego-networks interactivos de componentes de software críticos.
- **Distribución de Riesgo Sistémico**: Mapeo de clusters dominantes e impacto acumulativo.

## 📜 Licencia
Este proyecto es de código abierto, diseñado con fines académicos e investigativos.
