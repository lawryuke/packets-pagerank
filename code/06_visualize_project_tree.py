"""
Module to build an interactive dependency tree visualizer for specific packages.
"""
import polars as pl
import networkx as nx
from pyvis.network import Network
from pathlib import Path
import sys

PROCESSED_DIR = Path("../dataset_parquet")

def build_tree_visualizer(base_packages):
    """Generates an HTML interactive visualization of a project's dependency tree."""
    df_deps = pl.read_parquet(PROCESSED_DIR / "pypi_dependencies.parquet")
    df_projects = pl.read_parquet(PROCESSED_DIR / "pypi_projects.parquet")
    
    mapping_df = df_projects.select([
        pl.col("Name").str.to_lowercase().alias("pypi_name"),
        pl.col("Repository Name with Owner").str.to_lowercase().alias("repo_name")
    ]).drop_nulls()
    
    df_deps = df_deps.with_columns([
        pl.col("Repository Name with Owner").str.to_lowercase().alias("source"),
        pl.col("Dependency Project Name").str.to_lowercase().alias("target_pypi")
    ]).join(mapping_df, left_on="target_pypi", right_on="pypi_name", how="left")
    
    df_deps = df_deps.with_columns(
        pl.col("repo_name").fill_null(pl.col("target_pypi")).alias("target")
    )
    
    G = nx.DiGraph()
    G.add_edges_from(list(zip(df_deps["source"].to_list(), df_deps["target"].to_list())))
    
    tree_nodes, actual_roots = set(), set()
    for pkg in base_packages:
        pkg_lower = pkg.lower()
        matched_nodes = [n for n in G.nodes() if n == pkg_lower or (isinstance(n, str) and n.endswith(f"/{pkg_lower}"))]
        
        if matched_nodes:
            best_node = max(matched_nodes, key=lambda n: G.out_degree(n))
            actual_roots.add(best_node)
            tree_nodes.update(set(nx.descendants(G, best_node)) | {best_node})
            
    G_sub = G.subgraph(tree_nodes)
    
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    net.set_options("""
    var options = {
      "configure": {"enabled": true, "filter": ["layout", "physics"]},
      "layout": {"hierarchical": {"enabled": true, "direction": "LR", "nodeSpacing": 40, "treeSpacing": 50, "levelSeparation": 200, "blockShifting": true, "edgeMinimization": true, "parentCentralization": true}},
      "physics": {"enabled": false}
    }
    """)
    
    node_levels = {}
    for root in actual_roots:
        if root in G_sub:
            for n, dist in nx.single_source_shortest_path_length(G_sub, root).items():
                node_levels[n] = min(node_levels.get(n, float('inf')), dist)
                    
    for node in G_sub.nodes():
        lvl = node_levels.get(node, 0)
        if node in actual_roots:
            net.add_node(node, label=f"★ {node}", color="#ff4a4a", size=25, shape="dot", level=lvl)
        elif G_sub.out_degree(node) == 0:
            net.add_node(node, label=node, color="#4a90e2", size=10, shape="dot", level=lvl)
        else:
            net.add_node(node, label=node, color="#f5a623", size=15, shape="dot", level=lvl)
            
    for source, target in G_sub.edges():
        net.add_edge(source, target, color="#777777")
        
    out_file = "project_dependency_tree.html"
    net.write_html(out_file)
    
    custom_js = """
    <script type="text/javascript">
    setTimeout(function() {
        if (typeof network !== 'undefined') {
            var currentlySelectedNode = null;
            network.on("click", function (params) {
                network.setOptions({ layout: { hierarchical: { enabled: false } } });
                if (params.nodes.length > 0) {
                    var clickedNode = params.nodes[0];
                    if (clickedNode === currentlySelectedNode) {
                        currentlySelectedNode = null;
                        network.unselectAll();
                        nodes.update(nodes.get().map(n => ({id: n.id, color: n.originalColor, font: {color: "white"}})));
                        edges.update(edges.get().map(e => ({id: e.id, hidden: false})));
                        return;
                    }
                    currentlySelectedNode = clickedNode;
                    var connected = network.getConnectedNodes(clickedNode).concat(clickedNode);
                    nodes.update(nodes.get().map(n => {
                        if (!n.originalColor) n.originalColor = n.color;
                        return {id: n.id, color: connected.includes(n.id) ? n.originalColor : "rgba(0,0,0,0)", font: {color: connected.includes(n.id) ? "white" : "rgba(0,0,0,0)"}};
                    }));
                    edges.update(edges.get().map(e => ({id: e.id, hidden: !(e.from === clickedNode || e.to === clickedNode)})));
                } else {
                    currentlySelectedNode = null;
                    nodes.update(nodes.get().map(n => ({id: n.id, color: n.originalColor, font: {color: "white"}})));
                    edges.update(edges.get().map(e => ({id: e.id, hidden: false})));
                }
            });
        }
    }, 1000);
    </script>
    </body>
    """
    with open(out_file, "r") as f:
        html_content = f.read().replace("</body>", custom_js)
    with open(out_file, "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    MIS_PAQUETES = sys.argv[1:] if len(sys.argv) > 1 else ["requests", "Django", "Flask"]
    build_tree_visualizer(MIS_PAQUETES)
