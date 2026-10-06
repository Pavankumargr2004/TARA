import networkx as nx
# pyrefly: ignore [missing-import]
from pyvis.network import Network
from typing import List, Dict

class GraphBuilder:
    @staticmethod
    def build_attack_graph(threats: List[dict]) -> str:
        G = nx.DiGraph()
        
        for t in threats:
            path = t.get("attack_path", [])
            for i in range(len(path) - 1):
                source = path[i]
                target = path[i+1]
                G.add_node(source, color="#00B2E2", size=20)
                G.add_node(target, color="#10B981", size=20)
                G.add_edge(source, target, label="Exploit Path")
                
        net = Network(height="400px", width="100%", bgcolor="#F8FAFC", font_color="#0F172A", directed=True)
        net.from_nx(G)
        net.set_options('{"physics": {"barnesHut": {"springLength": 160}}}')
        return net.generate_html()
