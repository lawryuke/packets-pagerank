import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuraciones de estilo
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12})

PROCESSED_DIR = Path("../dataset_parquet")
RESULTS_FILE = PROCESSED_DIR / "pagerank_results.csv"

def main():
    print("Cargando resultados de PageRank...")
    if not RESULTS_FILE.exists():
        print(f"Error: No se encontró {RESULTS_FILE}")
        return

    df = pd.read_csv(RESULTS_FILE)

    # Agrupar por Cluster
    cluster_stats = df.groupby('Cluster').agg(
        Total_PageRank=('PageRank', 'sum'),
        Package_Count=('Package', 'count')
    ).reset_index()

    # Calcular porcentaje de PageRank (riesgo) que concentra cada cluster
    # Sabemos que la suma total de PageRank es 1.0 (o muy cercano)
    total_pr = cluster_stats['Total_PageRank'].sum()
    cluster_stats['Risk_Percentage'] = (cluster_stats['Total_PageRank'] / total_pr) * 100

    # Ordenar por el riesgo total que concentran
    cluster_stats = cluster_stats.sort_values(by='Total_PageRank', ascending=False).reset_index(drop=True)

    # Para identificar la "temática" de cada cluster, buscamos sus paquetes líderes
    print("\n--- TOP CLUSTERS POR RIESGO SISTÉMICO (PageRank Acumulado) ---")
    
    top_n_clusters = 10
    top_clusters = cluster_stats.head(top_n_clusters).copy()
    
    # Imprimir detalles para los Top 5 clusters (para bautizarlos en el TIF)
    for index, row in top_clusters.head(5).iterrows():
        c_id = row['Cluster']
        pct = row['Risk_Percentage']
        count = row['Package_Count']
        
        # Obtener los 5 paquetes más importantes de ese cluster
        c_packages = df[df['Cluster'] == c_id].sort_values('PageRank', ascending=False).head(5)
        top_pkg_names = ", ".join(c_packages['Package'].tolist())
        
        print(f"\nCluster ID: {c_id:.0f} | Concentra el {pct:.2f}% del Riesgo | Tamaño: {count:,.0f} paquetes")
        print(f"Paquetes Líderes: {top_pkg_names}")

    # --- Generar Gráfico Visual ---
    print("\nGenerando gráfico de distribución de riesgo por comunidades...")
    
    # Añadir etiquetas descriptivas para el gráfico (temporales, basadas en los líderes)
    # Como el algoritmo es no determinista, nombraremos los clusters por su paquete #1
    cluster_labels = []
    for c_id in top_clusters['Cluster']:
        top_pkg = df[df['Cluster'] == c_id].sort_values('PageRank', ascending=False).iloc[0]['Package']
        cluster_labels.append(f"Cluster {c_id:.0f}\n(ej. {top_pkg})")
    
    top_clusters['Label'] = cluster_labels

    plt.figure(figsize=(12, 7))
    ax = sns.barplot(
        data=top_clusters,
        x='Risk_Percentage',
        y='Label',
        palette='viridis'
    )
    
    plt.title('Concentración de Riesgo Sistémico por Comunidades (Top 10)', pad=20, fontweight='bold')
    plt.xlabel('Porcentaje del PageRank Total (%)')
    plt.ylabel('Comunidad (Cluster)')
    
    # Añadir el porcentaje en las barras
    for p in ax.patches:
        width = p.get_width()
        plt.text(width + 0.2, p.get_y() + p.get_height()/2. + 0.1, 
                 f'{width:.1f}%', ha="left")

    plt.tight_layout()
    plot_path = "cluster_risk_distribution.png"
    plt.savefig(plot_path, dpi=300)
    print(f"¡Gráfico guardado exitosamente en {plot_path}!")

if __name__ == "__main__":
    main()
