import pandas as pd
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

PROCESSED_DIR = Path("../dataset_parquet")

def visualize_core():
    # Como no tenemos el CSV (porque no se volvió a ejecutar el script 04),
    # usaremos los paquetes críticos (Top 10 y anomalías) extraídos de result_temp.txt
    core_packages = [
        "requests", "Django", "Flask", "numpy", "six", "pytest", 
        "setuptools", "django", "flask", "boto",
        "larsjsol/shellpic", "uber/ludwig", "explosion/spacy-stanfordnlp", 
        "ewjoachim/restaurants-api", "yuhui/landtransportsg"
    ]
    
    print("Cargando dependencias completas para extraer el subgrafo del Core...")
    df_deps = pl.read_parquet(PROCESSED_DIR / "pypi_dependencies.parquet")
    
    # Filtrar aristas donde el origen o el destino estén en nuestro core
    # Esto nos dará el ego-network (vecindario directo) de los paquetes críticos
    edges = df_deps.filter(
        (pl.col("Repository Name with Owner").is_in(core_packages)) |
        (pl.col("Dependency Project Name").is_in(core_packages))
    )
    
    edges_list = list(zip(
        edges["Repository Name with Owner"].to_list(),
        edges["Dependency Project Name"].to_list()
    ))
    
    print(f"Construyendo subgrafo con {len(edges_list)} aristas...")
    G = nx.DiGraph()
    G.add_edges_from(edges_list)
    
    # Para la visualización, si el vecindario es muy grande, lo filtramos un poco
    # Nos quedamos con los nodos de mayor grado en este subgrafo
    degrees = dict(G.degree())
    # Ordenar nodos por grado y quedarnos con los top 150
    top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:150]
    G_sub = G.subgraph(top_nodes)
    
    print("Generando visualización...")
    plt.figure(figsize=(18, 14))
    
    # Layout (posiciones)
    pos = nx.spring_layout(G_sub, k=0.8, iterations=100, seed=42)
    
    # Tamaños de nodos proporcionales al in-degree local
    in_degrees = dict(G_sub.in_degree())
    max_in = max(in_degrees.values()) if in_degrees else 1
    node_sizes = [5000 * (in_degrees.get(node, 0) / max_in) + 150 for node in G_sub.nodes()]
    
    # Colores: rojo para los paquetes críticos (anomalías/top10), azul para el resto
    colors = ['#ff7f0e' if node in core_packages else '#1f77b4' for node in G_sub.nodes()]
    
    # Dibujar nodos
    nx.draw_networkx_nodes(G_sub, pos, node_size=node_sizes, node_color=colors, 
                           alpha=0.9, edgecolors='white', linewidths=1.5)
    
    # Dibujar aristas
    nx.draw_networkx_edges(G_sub, pos, alpha=0.2, edge_color='gray', 
                           arrows=True, arrowsize=10, connectionstyle='arc3,rad=0.15')
    
    # Dibujar etiquetas solo para los nodos más importantes o del core
    labels = {node: node for node in G_sub.nodes() if node in core_packages or in_degrees.get(node,0) > max_in*0.2}
    nx.draw_networkx_labels(G_sub, pos, labels=labels, font_size=9, font_weight='bold')
    
    plt.title(f"Red de Impacto Local: Top Paquetes y Anomalías (Vecindario)", fontsize=22, pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    out_file = "pypi_core_graph.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"¡Visualización guardada con éxito en {out_file}!")

if __name__ == "__main__":
    visualize_core()
