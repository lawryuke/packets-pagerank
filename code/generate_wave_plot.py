"""
Module to generate the wave plot visualizing the systemic propagation of risk.
"""
import matplotlib.pyplot as plt
import numpy as np

def generate_plot():
    """Generates and saves the wave plot using static dataset points."""
    paquetes = ['requests', '+ Django', '+ Flask', '+ numpy', '+ six', 
                '+ pytest', '+ setuptools', '+ django', '+ flask', '+ boto']
    porcentajes_acumulados = [17.64, 25.38, 31.68, 38.69, 41.60, 44.99, 46.92, 48.93, 50.26, 51.23]

    plt.figure(figsize=(12, 6))
    plt.style.use('default')
    x = np.arange(len(paquetes))

    plt.plot(x, porcentajes_acumulados, color='#a10000', linewidth=3, marker='o', markersize=8)
    plt.fill_between(x, porcentajes_acumulados, color='#a10000', alpha=0.3)
    plt.fill_between(x, porcentajes_acumulados, 100, color='#e0e0e0', alpha=0.3)

    for i, txt in enumerate(porcentajes_acumulados):
        plt.annotate(f"{txt}%", (x[i], porcentajes_acumulados[i]), 
                     textcoords="offset points", xytext=(0,10), ha='center',
                     fontweight='bold', fontsize=10)

    plt.title('Propagación Sistémica: Onda Expansiva (Top 10)', fontsize=16, pad=20, fontweight='bold')
    plt.ylabel('Porcentaje del Ecosistema PyPI Comprometido', fontsize=12)
    plt.xlabel('Paquetes', fontsize=12)
    
    plt.ylim(0, 100)
    plt.xticks(x, paquetes, rotation=45, ha='right')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig("onda_expansiva.png", dpi=300)

if __name__ == "__main__":
    generate_plot()
