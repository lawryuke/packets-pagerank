"""
Module to analyze PageRank results and visualize the risk distribution across communities.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12})

PROCESSED_DIR = Path("../dataset_parquet")
RESULTS_FILE = PROCESSED_DIR / "pagerank_results.csv"

def main():
    """Generates clustering stats and visualizes community risk concentration."""
    if not RESULTS_FILE.exists():
        print(f"Error: No se encontró {RESULTS_FILE}")
        return

    df = pd.read_csv(RESULTS_FILE)
    
    cluster_stats = df.groupby('Cluster').agg(
        Total_PageRank=('PageRank', 'sum'),
        Package_Count=('Package', 'count')
    ).reset_index()

    total_pr = cluster_stats['Total_PageRank'].sum()
    cluster_stats['Risk_Percentage'] = (cluster_stats['Total_PageRank'] / total_pr) * 100
    cluster_stats = cluster_stats.sort_values(by='Total_PageRank', ascending=False).reset_index(drop=True)

    top_clusters = cluster_stats.head(10).copy()
    
    for _, row in top_clusters.head(5).iterrows():
        c_packages = df[df['Cluster'] == row['Cluster']].sort_values('PageRank', ascending=False).head(5)
        print(f"Cluster ID: {row['Cluster']:.0f} | Riesgo: {row['Risk_Percentage']:.2f}% | Tamaño: {row['Package_Count']:,.0f}")
        print(f"Paquetes Líderes: {', '.join(c_packages['Package'].tolist())}\n")

    top_clusters['Label'] = [
        f"Cluster {c_id:.0f}\n({df[df['Cluster'] == c_id].sort_values('PageRank', ascending=False).iloc[0]['Package']})"
        for c_id in top_clusters['Cluster']
    ]

    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=top_clusters, x='Risk_Percentage', y='Label', palette='viridis')
    
    plt.title('Concentración de Riesgo Sistémico por Comunidades', pad=20, fontweight='bold')
    plt.xlabel('Porcentaje del PageRank Total (%)')
    plt.ylabel('Comunidad (Cluster)')
    
    for p in ax.patches:
        plt.text(p.get_width() + 0.2, p.get_y() + p.get_height()/2. + 0.1, f'{p.get_width():.1f}%', ha="left")

    plt.tight_layout()
    plt.savefig("cluster_risk_distribution.png", dpi=300)

if __name__ == "__main__":
    main()
