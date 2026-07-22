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
    print("1. Cargando datos de PyPI (previamente filtrados)...")
    
    deps_file = PROCESSED_DIR / "pypi_dependencies.parquet"
    if not deps_file.exists():
        raise FileNotFoundError("Ejecuta 03_filter_pypi.py primero para crear pypi_dependencies.parquet")
    
    df_deps = pl.read_parquet(deps_file)
    
    # Construir el grafo dirigido
    print("2. Construyendo grafo dirigido con NetworkX...")
    G = nx.DiGraph()
    
    # La arista (A -> B) indica que A depende de B
    edges = list(zip(df_deps["Repository Name with Owner"], df_deps["Dependency Project Name"]))
    G.add_edges_from(edges)
    
    return G

def analyze_topology(G):
    print("\n--- 4.1 Topología del grafo de dependencias ---")
    n = G.number_of_nodes()
    m = G.number_of_edges()
    density = nx.density(G)
    
    print(f"Número de nodos (paquetes activos): {n}")
    print(f"Número de aristas (dependencias runtime): {m}")
    print(f"Densidad: {density:.6e}")
    
    # Paquetes sin dependencias salientes (dangling nodes)
    # out_degree indica a cuántos paquetes apunta (depende de)
    out_degrees = dict(G.out_degree())
    dangling_nodes = sum(1 for v, d in out_degrees.items() if d == 0)
    print(f"Paquetes sin dependencias salientes: {dangling_nodes} ({(dangling_nodes/n)*100:.2f}%)")
    
    # GSCC (Giant Strongly Connected Component)
    print("Calculando componente fuertemente conexa (GSCC)...")
    gscc_nodes = max(nx.strongly_connected_components(G), key=len)
    print(f"Tamaño GSCC / total: {len(gscc_nodes)} / {n} ({(len(gscc_nodes)/n)*100:.2f}%)")
    
    # Ley de potencias en In-degree
    print("Ajustando distribución de grado (Ley de potencias)...")
    in_degrees = [d for n, d in G.in_degree() if d > 0]
    fit = powerlaw.Fit(in_degrees, discrete=True, verbose=False)
    gamma = fit.power_law.alpha
    print(f"Exponente ley de potencias gamma: {gamma:.2f}")

def build_transition_matrix(G):
    print("\nConstruyendo Matriz de Transición H...")
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    idx = {node: i for i, node in enumerate(nodes)}
    
    rows, cols, data = [], [], []
    dangling = []
    
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
    n = H.shape[0]
    r = np.full(n, 1.0 / n)
    
    for k in range(max_iter):
        dangling_contrib = d * (a @ r) / n
        r_new = d * H.dot(r) + dangling_contrib + (1.0 - d) / n
        err = np.abs(r_new - r).sum()
        r = r_new
        if err < eps:
            return r, k + 1
            
    return r, max_iter

def convergence_analysis(H, a, nodes):
    print("\n--- 4.2 Convergencia del método de la potencia ---")
    d_values = [0.75, 0.85, 0.90, 0.95]
    for d in d_values:
        _, iters = pagerank_power(H, a, nodes, d=d, eps=1e-8)
        print(f"d={d:.2f} -> Convergencia en {iters} iteraciones")

def analyze_centrality_and_communities(G, H, a, nodes):
    print("\n--- 4.3 Ranking de paquetes críticos ---")
    print("Calculando PageRank final con d=0.85...")
    r_final, _ = pagerank_power(H, a, nodes, d=0.85)
    
    # Crear DataFrame con resultados
    df_results = pd.DataFrame({
        'Package': nodes,
        'PageRank': r_final,
        'InDegree': [d for n, d in G.in_degree(nodes)]
    })
    
    print("Calculando comunidades (Louvain) en el grafo no dirigido...")
    # Esto puede tardar varios minutos
    G_undirected = G.to_undirected()
    partition = community_louvain.best_partition(G_undirected)
    df_results['Cluster'] = df_results['Package'].map(partition)
    
    # Ordenar por PageRank
    df_results = df_results.sort_values(by='PageRank', ascending=False).reset_index(drop=True)
    df_results['PR_Rank'] = df_results.index + 1
    
    # Ordenar por InDegree
    df_indegree = df_results.sort_values(by='InDegree', ascending=False).reset_index(drop=True)
    
    # Mapeo In-degree Rank
    in_deg_rank_map = {row['Package']: i+1 for i, row in df_indegree.iterrows()}
    df_results['InDeg_Rank'] = df_results['Package'].map(in_deg_rank_map)
    
    print("\nTop 10 Paquetes por PageRank:")
    print(df_results[['PR_Rank', 'Package', 'Cluster', 'PageRank', 'InDegree']].head(10).to_string(index=False))
    
    print("\n--- 4.4 Divergencia PageRank vs. in-degree ---")
    rho, pval = spearmanr(df_results['PageRank'], df_results['InDegree'])
    print(f"Correlación de Spearman (PageRank vs In-Degree): rho = {rho:.4f}")
    
    # Anomalias: Alto PageRank, Bajo In-degree (Rankings difieren mucho)
    df_results['Rank_Diff'] = df_results['InDeg_Rank'] - df_results['PR_Rank']
    anomalies = df_results.sort_values(by='Rank_Diff', ascending=False).head(5)
    print("\nPaquetes con riesgo transitivo oculto (Alto PR, Bajo In-Degree):")
    print(anomalies[['Package', 'PR_Rank', 'InDeg_Rank', 'Rank_Diff']].to_string(index=False))
    
    # Guardar resultados en un archivo CSV
    results_file = PROCESSED_DIR / "pagerank_results.csv"
    df_results.to_csv(results_file, index=False)
    print(f"\n¡Resultados completos guardados exitosamente en {results_file}!")
    
    return df_results.head(10)['Package'].tolist()

def analyze_transitive_coverage(G, top_packages):
    print("\n--- 4.5 Análisis de cobertura transitiva ---")
    print("Calculando cobertura transitiva individual y acumulada...")
    G_rev = G.reverse()
    
    covered_nodes_accum = set()
    n = G.number_of_nodes()
    
    print("\nCobertura Transitiva (Individual vs Acumulada):")
    print(f"{'Top':<4} | {'Paquete':<20} | {'Indiv. Nodos':<12} | {'% Indiv.':<10} | {'Acum. Nodos':<12} | {'% Acum.':<10}")
    print("-" * 85)
    
    for i, pkg in enumerate(top_packages, 1):
        indiv_covered = set()
        if pkg in G_rev:
            # descendants en el grafo invertido son los paquetes que dependen de `pkg`
            reachable = nx.descendants(G_rev, pkg)
            indiv_covered.update(reachable)
            indiv_covered.add(pkg)
            
            # Acumulado
            covered_nodes_accum.update(indiv_covered)
            
        indiv_pct = (len(indiv_covered) / n) * 100
        accum_pct = (len(covered_nodes_accum) / n) * 100
        
        print(f"{i:<4} | {pkg:<20} | {len(indiv_covered):<12} | {indiv_pct:>7.2f}% | {len(covered_nodes_accum):<12} | {accum_pct:>7.2f}%")
        
    print(f"\nEn total, los Top 10 paquetes cubren transitivamente {len(covered_nodes_accum)} paquetes.")
    print(f"Esto representa el {(len(covered_nodes_accum) / n) * 100:.2f}% de todo el ecosistema PyPI activo.")

def main():
    start_time = time.time()
    
    # 1. Cargar Grafo
    G = load_pypi_graph()
    
    # 2. Análisis Topológico
    analyze_topology(G)
    
    # 3. Matriz de Transición
    H, a, nodes = build_transition_matrix(G)
    
    # 4. Convergencia de PageRank
    convergence_analysis(H, a, nodes)
    
    # 5. Ranking y Comunidades
    top_10_packages = analyze_centrality_and_communities(G, H, a, nodes)
    
    # 6. Cobertura transitiva
    analyze_transitive_coverage(G, top_10_packages)
    
    elapsed = time.time() - start_time
    print(f"\n¡Análisis completado en {elapsed/60:.2f} minutos!")

if __name__ == "__main__":
    main()
