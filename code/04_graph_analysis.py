"""
Graph analysis module for computing PageRank and topological properties of PyPI dependencies.
"""
import pandas as pd
import polars as pl
import networkx as nx
import scipy.sparse as sp
import numpy as np
import powerlaw
import community as community_louvain
from pathlib import Path
from scipy.stats import spearmanr
import time

PROCESSED_DIR = Path("../dataset_parquet")

def load_pypi_graph():
    """Loads PyPI dependencies and constructs a directed graph."""
    deps_file = PROCESSED_DIR / "pypi_dependencies.parquet"
    if not deps_file.exists():
        raise FileNotFoundError("Ejecuta 03_filter_pypi.py primero para crear pypi_dependencies.parquet")
    
    df_deps = pl.read_parquet(deps_file)
    G = nx.DiGraph()
    edges = list(zip(df_deps["Repository Name with Owner"], df_deps["Dependency Project Name"]))
    G.add_edges_from(edges)
    return G

def analyze_topology(G):
    """Analyzes and prints topological metrics of the graph."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    
    print(f"Nodos: {n} | Aristas: {m} | Densidad: {nx.density(G):.6e}")
    
    out_degrees = dict(G.out_degree())
    dangling_nodes = sum(1 for v, d in out_degrees.items() if d == 0)
    print(f"Paquetes sin dependencias salientes: {dangling_nodes} ({(dangling_nodes/n)*100:.2f}%)")
    
    gscc_nodes = max(nx.strongly_connected_components(G), key=len)
    print(f"Tamaño GSCC: {len(gscc_nodes)} ({(len(gscc_nodes)/n)*100:.2f}%)")
    
    in_degrees = [d for n, d in G.in_degree() if d > 0]
    fit = powerlaw.Fit(in_degrees, discrete=True, verbose=False)
    print(f"Exponente ley de potencias gamma: {fit.power_law.alpha:.2f}")

def build_transition_matrix(G):
    """Builds the transition matrix for PageRank calculation."""
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    idx = {node: i for i, node in enumerate(nodes)}
    
    rows, cols, data, dangling = [], [], [], []
    for j, node in enumerate(nodes):
        out_neighbors = list(G.successors(node))
        if out_neighbors:
            w = 1.0 / len(out_neighbors)
            for nb in out_neighbors:
                rows.append(idx[nb])
                cols.append(j)
                data.append(w)
        else:
            dangling.append(j)
            
    H = sp.csr_matrix((data, (rows, cols)), shape=(n, n))
    a = np.zeros(n)
    a[dangling] = 1.0
    return H, a, nodes

def pagerank_power(H, a, nodes, d=0.85, eps=1e-8, max_iter=500):
    """Computes PageRank using the power iteration method."""
    n = H.shape[0]
    r = np.full(n, 1.0 / n)
    for k in range(max_iter):
        dangling_contrib = d * (a @ r) / n
        r_new = d * H.dot(r) + dangling_contrib + (1.0 - d) / n
        if np.abs(r_new - r).sum() < eps:
            return r_new, k + 1
        r = r_new
    return r, max_iter

def convergence_analysis(H, a, nodes):
    """Analyzes PageRank convergence for different damping factors."""
    for d in [0.75, 0.85, 0.90, 0.95]:
        _, iters = pagerank_power(H, a, nodes, d=d, eps=1e-8)
        print(f"d={d:.2f} -> Convergencia en {iters} iteraciones")

def analyze_centrality_and_communities(G, H, a, nodes):
    """Ranks nodes by PageRank, detects communities, and identifies anomalies."""
    r_final, _ = pagerank_power(H, a, nodes, d=0.85)
    
    df_results = pd.DataFrame({
        'Package': nodes,
        'PageRank': r_final,
        'InDegree': [d for n, d in G.in_degree(nodes)]
    })
    
    G_undirected = G.to_undirected()
    df_results['Cluster'] = df_results['Package'].map(community_louvain.best_partition(G_undirected))
    
    df_results = df_results.sort_values(by='PageRank', ascending=False).reset_index(drop=True)
    df_results['PR_Rank'] = df_results.index + 1
    
    df_indegree = df_results.sort_values(by='InDegree', ascending=False).reset_index(drop=True)
    in_deg_rank_map = {row['Package']: i+1 for i, row in df_indegree.iterrows()}
    df_results['InDeg_Rank'] = df_results['Package'].map(in_deg_rank_map)
    
    print("\nTop 10 Paquetes por PageRank:")
    print(df_results[['PR_Rank', 'Package', 'Cluster', 'PageRank', 'InDegree']].head(10).to_string(index=False))
    
    rho, _ = spearmanr(df_results['PageRank'], df_results['InDegree'])
    print(f"\nCorrelación de Spearman (PageRank vs In-Degree): rho = {rho:.4f}")
    
    df_results['Rank_Diff'] = df_results['InDeg_Rank'] - df_results['PR_Rank']
    print("\nPaquetes con riesgo transitivo oculto:")
    print(df_results.sort_values(by='Rank_Diff', ascending=False).head(5)[['Package', 'PR_Rank', 'InDeg_Rank', 'Rank_Diff']].to_string(index=False))
    
    results_file = PROCESSED_DIR / "pagerank_results.csv"
    df_results.to_csv(results_file, index=False)
    return df_results.head(10)['Package'].tolist()

def analyze_transitive_coverage(G, top_packages):
    """Analyzes the transitive coverage of top packages."""
    G_rev = G.reverse()
    covered_nodes_accum = set()
    n = G.number_of_nodes()
    
    print("\nCobertura Transitiva (Individual vs Acumulada):")
    for i, pkg in enumerate(top_packages, 1):
        indiv_covered = set(nx.descendants(G_rev, pkg)) | {pkg} if pkg in G_rev else set()
        covered_nodes_accum.update(indiv_covered)
        print(f"{i:<4} | {pkg:<20} | Indiv: {len(indiv_covered):<8} Acum: {len(covered_nodes_accum)}")

def main():
    start_time = time.time()
    G = load_pypi_graph()
    analyze_topology(G)
    H, a, nodes = build_transition_matrix(G)
    convergence_analysis(H, a, nodes)
    top_10_packages = analyze_centrality_and_communities(G, H, a, nodes)
    analyze_transitive_coverage(G, top_10_packages)
    print(f"\nAnálisis completado en {(time.time() - start_time)/60:.2f} minutos.")

if __name__ == "__main__":
    main()
