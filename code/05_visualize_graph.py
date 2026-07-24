"""
Module to visualize the ego-network core of critical dependencies.
"""
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

PROCESSED_DIR = Path("../dataset_parquet")

def visualize_core():
    """Generates a visualization of the core dependencies graph."""
    core_packages = [
        "requests", "Django", "Flask", "numpy", "six", "pytest", 
        "setuptools", "django", "flask", "boto",
        "larsjsol/shellpic", "uber/ludwig", "explosion/spacy-stanfordnlp", 
        "ewjoachim/restaurants-api", "yuhui/landtransportsg"
    ]
    
    df_deps = pl.read_parquet(PROCESSED_DIR / "pypi_dependencies.parquet")
    
    edges = df_deps.filter(
        (pl.col("Repository Name with Owner").is_in(core_packages)) |
        (pl.col("Dependency Project Name").is_in(core_packages))
    )
    
    edges_list = list(zip(
        edges["Repository Name with Owner"].to_list(),
        edges["Dependency Project Name"].to_list()
    ))
    
    G = nx.DiGraph()
    G.add_edges_from(edges_list)
    
    degrees = dict(G.degree())
    top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:150]
    G_sub = G.subgraph(top_nodes)
    
    plt.figure(figsize=(18, 14))
    pos = nx.spring_layout(G_sub, k=0.8, iterations=100, seed=42)
    
    in_degrees = dict(G_sub.in_degree())
    max_in = max(in_degrees.values()) if in_degrees else 1
    node_sizes = [5000 * (in_degrees.get(node, 0) / max_in) + 150 for node in G_sub.nodes()]
    colors = ['#ff7f0e' if node in core_packages else '#1f77b4' for node in G_sub.nodes()]
    
    nx.draw_networkx_nodes(G_sub, pos, node_size=node_sizes, node_color=colors, alpha=0.9, edgecolors='white', linewidths=1.5)
    nx.draw_networkx_edges(G_sub, pos, alpha=0.2, edge_color='gray', arrows=True, arrowsize=10, connectionstyle='arc3,rad=0.15')
    
    labels = {node: node for node in G_sub.nodes() if node in core_packages or in_degrees.get(node,0) > max_in*0.2}
    nx.draw_networkx_labels(G_sub, pos, labels=labels, font_size=9, font_weight='bold')
    
    plt.title(f"Red de Impacto Local: Top Paquetes y Anomalías", fontsize=22, pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig("pypi_core_graph.png", dpi=300, bbox_inches='tight', facecolor='white')

if __name__ == "__main__":
    visualize_core()
