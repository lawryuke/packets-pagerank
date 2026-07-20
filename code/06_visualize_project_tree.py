import polars as pl
import networkx as nx
from pyvis.network import Network
from pathlib import Path

PROCESSED_DIR = Path("../dataset_parquet")

def build_tree_visualizer(base_packages):
    print("Cargando todas las dependencias (puede tardar un momento)...")
    df_deps = pl.read_parquet(PROCESSED_DIR / "pypi_dependencies.parquet")
    df_projects = pl.read_parquet(PROCESSED_DIR / "pypi_projects.parquet")
    
    # Crear un diccionario de mapeo: Paquete PyPI (Name) -> Repositorio (Repository Name with Owner)
    # Convertimos a minúsculas para un cruce perfecto
    mapping_df = df_projects.select([
        pl.col("Name").str.to_lowercase().alias("pypi_name"),
        pl.col("Repository Name with Owner").str.to_lowercase().alias("repo_name")
    ]).drop_nulls()
    
    # Unir dependencias con proyectos para traducir el destino
    df_deps = df_deps.with_columns([
        pl.col("Repository Name with Owner").str.to_lowercase().alias("source"),
        pl.col("Dependency Project Name").str.to_lowercase().alias("target_pypi")
    ])
    
    df_deps = df_deps.join(mapping_df, left_on="target_pypi", right_on="pypi_name", how="left")
    
    # Si no encontramos el repo_name, mantenemos el pypi_name original (como fallback)
    df_deps = df_deps.with_columns(
        pl.col("repo_name").fill_null(pl.col("target_pypi")).alias("target")
    )
    
    # Crear grafo completo (dirigido: Proyecto -> Dependencia)
    edges_list = list(zip(
        df_deps["source"].to_list(),
        df_deps["target"].to_list()
    ))
    
    G = nx.DiGraph()
    G.add_edges_from(edges_list)
    print(f"Grafo base cargado: {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.")
    
    # Extraer el árbol de dependencias transitivas
    tree_nodes = set()
    actual_roots = set() # <--- GUARDAR LOS VERDADEROS NODOS RAÍZ
    for pkg in base_packages:
        pkg_lower = pkg.lower()
        # Buscar el nombre exacto del nodo en el grafo (puede tener un prefijo de dueño "owner/pkg")
        matched_nodes = [n for n in G.nodes() if n == pkg_lower or (isinstance(n, str) and n.endswith(f"/{pkg_lower}"))]
        
        if matched_nodes:
            # Tomamos el que tenga mayor out-degree por si hay colisiones
            best_node = max(matched_nodes, key=lambda n: G.out_degree(n))
            descendants = nx.descendants(G, best_node)
            
            actual_roots.add(best_node) # Lo guardamos como la raíz real
            tree_nodes.add(best_node)
            tree_nodes.update(descendants)
            print(f"[{best_node}] requiere {len(descendants)} dependencias transitivas.")
        else:
            print(f"Advertencia: El paquete '{pkg}' no se encontró en el dataset activo.")
            
    # Extraer el subgrafo con el árbol completo
    G_sub = G.subgraph(tree_nodes)
    print(f"Subgrafo final a visualizar: {G_sub.number_of_nodes()} nodos y {G_sub.number_of_edges()} aristas.")
    
    # Configurar PyVis
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    # Opciones avanzadas de Vis.js para layout jerárquico (red neuronal estática)
    net.set_options("""
    var options = {
      "configure": {
        "enabled": true,
        "filter": ["layout", "physics"]
      },
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "LR",
          "nodeSpacing": 40,
          "treeSpacing": 50,
          "levelSeparation": 200,
          "blockShifting": true,
          "edgeMinimization": true,
          "parentCentralization": true
        }
      },
      "physics": {
        "enabled": false
      }
    }
    """)
    
    # Calcular niveles manualmente (distancia mínima desde la raíz) para evitar huecos gigantes
    node_levels = {}
    for root in actual_roots:
        if root in G_sub:
            lengths = nx.single_source_shortest_path_length(G_sub, root)
            for n, dist in lengths.items():
                if n not in node_levels or dist < node_levels[n]:
                    node_levels[n] = dist
                    
    # Añadir nodos con estilos y NIVEL explícito
    for node in G_sub.nodes():
        lvl = node_levels.get(node, 0)
        if node in actual_roots:
            color = "#ff4a4a"
            size = 25
            label = f"★ {node}"
        elif G_sub.out_degree(node) == 0:
            color = "#4a90e2"
            size = 10
            label = node
        else:
            color = "#f5a623"
            size = 15
            label = node
            
        net.add_node(node, label=label, color=color, size=size, shape="dot", level=lvl)
        
    # Añadir aristas
    for source, target in G_sub.edges():
        net.add_edge(source, target, color="#777777")
        
    out_file = "project_dependency_tree.html"
    # Guardar archivo
    net.write_html(out_file)
    
    # Inyectar JavaScript personalizado para ocultar nodos no conectados al hacer click
    with open(out_file, "r") as f:
        html_content = f.read()
        
    custom_js = """
    <script type="text/javascript">
    // Esperar a que el grafo cargue
    setTimeout(function() {
        if (typeof network !== 'undefined') {
            var currentlySelectedNode = null;
            
            network.on("click", function (params) {
                // APAGAR el motor jerárquico en el primer clic para congelar las posiciones (x,y) actuales
                // Así evitamos que al cambiar colores se recalcule el árbol y salte la pantalla
                network.setOptions({ layout: { hierarchical: { enabled: false } } });
                
                if (params.nodes.length > 0) {
                    var clickedNode = params.nodes[0];
                    
                    if (clickedNode === currentlySelectedNode) {
                        // Toggle: clic en el mismo nodo restaura todo
                        currentlySelectedNode = null;
                        network.unselectAll();
                        
                        var allNodes = nodes.get();
                        var nodeUpdates = [];
                        for (var i = 0; i < allNodes.length; i++) {
                            var n = allNodes[i];
                            if (n.originalColor) {
                                nodeUpdates.push({id: n.id, color: n.originalColor, font: {color: "white"}});
                            }
                        }
                        nodes.update(nodeUpdates);
                        
                        var allEdges = edges.get();
                        var edgeUpdates = [];
                        for (var i = 0; i < allEdges.length; i++) {
                            edgeUpdates.push({id: allEdges[i].id, hidden: false});
                        }
                        edges.update(edgeUpdates);
                        return; // Salir de la función
                    }
                    
                    // Click en un nuevo nodo: Aislar
                    currentlySelectedNode = clickedNode;
                    var connectedNodes = network.getConnectedNodes(clickedNode);
                    connectedNodes.push(clickedNode);
                    
                    // Actualizar Nodos (hacerlos invisibles sin removerlos del motor matemático)
                    var allNodes = nodes.get();
                    var nodeUpdates = [];
                    for (var i = 0; i < allNodes.length; i++) {
                        var n = allNodes[i];
                        if (!n.originalColor) n.originalColor = n.color;
                        
                        var isConnected = false;
                        for (var j = 0; j < connectedNodes.length; j++) {
                            if (String(connectedNodes[j]) === String(n.id)) {
                                isConnected = true;
                                break;
                            }
                        }
                        
                        if (isConnected) {
                            nodeUpdates.push({id: n.id, color: n.originalColor, font: {color: "white"}});
                        } else {
                            nodeUpdates.push({id: n.id, color: "rgba(0,0,0,0)", font: {color: "rgba(0,0,0,0)"}});
                        }
                    }
                    nodes.update(nodeUpdates);
                    
                    // Actualizar Aristas
                    var allEdges = edges.get();
                    var edgeUpdates = [];
                    for (var i = 0; i < allEdges.length; i++) {
                        var e = allEdges[i];
                        if (String(e.from) === String(clickedNode) || String(e.to) === String(clickedNode)) {
                            edgeUpdates.push({id: e.id, hidden: false});
                        } else {
                            edgeUpdates.push({id: e.id, hidden: true});
                        }
                    }
                    edges.update(edgeUpdates);
                    
                } else {
                    // Click en el fondo: restaurar todo
                    currentlySelectedNode = null;
                    var allNodes = nodes.get();
                    var nodeUpdates = [];
                    for (var i = 0; i < allNodes.length; i++) {
                        var n = allNodes[i];
                        if (n.originalColor) {
                            nodeUpdates.push({id: n.id, color: n.originalColor, font: {color: "white"}});
                        }
                    }
                    nodes.update(nodeUpdates);
                    
                    var allEdges = edges.get();
                    var edgeUpdates = [];
                    for (var i = 0; i < allEdges.length; i++) {
                        edgeUpdates.push({id: allEdges[i].id, hidden: false});
                    }
                    edges.update(edgeUpdates);
                }
            });
        }
    }, 1000);
    </script>
    </body>
    """
    html_content = html_content.replace("</body>", custom_js)
    
    with open(out_file, "w") as f:
        f.write(html_content)
        
    print(f"¡Grafo interactivo generado con éxito: {out_file}!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        MIS_PAQUETES = sys.argv[1:]
    else:
        # Paquetes por defecto conocidos
        MIS_PAQUETES = ["requests", "Django", "Flask"]
    
    print(f"Analizando árbol de dependencias para: {MIS_PAQUETES}")
    build_tree_visualizer(MIS_PAQUETES)
