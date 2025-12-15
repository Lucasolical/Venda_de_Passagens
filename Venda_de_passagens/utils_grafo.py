import networkx as nx
import matplotlib
matplotlib.use('Agg') # Backend não-interativo para servidor
import matplotlib.pyplot as plt
import io
import base64
from igraph import Graph

# --- CONSTRUÇÃO DO GRAFO (IGRAPH - Para o Dijkstra) ---
def construir_grafo_voos(dados_voos):
    g = Graph(directed=True)
    cidades = set()
    for voo in dados_voos.values():
        cidades.add(voo['origem'].strip())
        cidades.add(voo['destino'].strip())
    
    cidade_lista = sorted(list(cidades))
    mapa_cidades_lower = {cidade.lower(): i for i, cidade in enumerate(cidade_lista)}
    
    g.add_vertices(len(cidade_lista))
    g.vs["label"] = cidade_lista
    
    arestas = []
    pesos_custo = []
    codigos_voo = []
    
    for codigo, voo in dados_voos.items():
        origem = voo['origem'].strip()
        destino = voo['destino'].strip()
        idx_origem = mapa_cidades_lower.get(origem.lower())
        idx_destino = mapa_cidades_lower.get(destino.lower())
        
        if idx_origem is not None and idx_destino is not None:
            arestas.append((idx_origem, idx_destino))
            pesos_custo.append(float(voo['preco']))
            codigos_voo.append(codigo)
            
    g.add_edges(arestas)
    g.es["preco"] = pesos_custo
    g.es["codigo"] = codigos_voo
    return g, mapa_cidades_lower

# --- BUSCA (IGRAPH) ---
def buscar_melhor_conexao(grafo, mapa_cidades, dados_voos, origem_str, destino_str):
    origem_buscada = origem_str.strip().lower()
    destino_buscada = destino_str.strip().lower()
    
    if origem_buscada not in mapa_cidades or destino_buscada not in mapa_cidades:
        cidades_disponiveis = ", ".join(grafo.vs["label"])
        return None, f"Cidade não encontrada. Disponíveis: {cidades_disponiveis}"
        
    idx_origem = mapa_cidades[origem_buscada]
    idx_destino = mapa_cidades[destino_buscada]
    
    # CORREÇÃO DA CHAMADA (v, to)
    caminho_indices = grafo.get_shortest_paths(
        v=idx_origem, 
        to=idx_destino, 
        weights=grafo.es["preco"], 
        # weights=grafo.es["milhas"], 
        # weights=None, 
        output="epath"
    )
    
    if not caminho_indices or not caminho_indices[0]:
        return None, "Nenhuma conexão encontrada entre essas cidades."
        
    epath = caminho_indices[0]
    trajeto = []
    custo_total = 0.0
    
    for edge_i in epath:
        aresta = grafo.es[edge_i]
        custo_total += aresta["preco"]
        origem_nome = grafo.vs[aresta.source]["label"]
        destino_nome = grafo.vs[aresta.target]["label"]
        trajeto.append({
            "origem": origem_nome,
            "destino": destino_nome,
            "codigo": aresta["codigo"],
            "preco": aresta["preco"],
            "milhas": dados_voos[aresta["codigo"]]['milhas']
        })
            
    return {"trajeto": trajeto, "custo_total": custo_total, "paradas": len(trajeto)-1}, "Rota encontrada!"

# --- GERAÇÃO VISUAL (NETWORKX) ---
def gerar_diagrama_grafo(dados_voos, trajeto=None):
    """
    Gera imagem do grafo completo.
    Se 'trajeto' for passado, destaca o caminho em VERMELHO.
    """
    G = nx.DiGraph()
    
    # Adicionar TODOS os voos ao grafo visual
    for codigo, voo in dados_voos.items():
        origem = voo['origem'].strip()
        destino = voo['destino'].strip()
        G.add_edge(origem, destino, label=f"{codigo}\nR${voo['preco']:.0f}")

    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42) 

    # Desenho Padrão
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2500)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15, width=1, alpha=0.5)
    
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='gray', font_size=7)

    # Destaque
    if trajeto:
        arestas_rota = []
        nodos_rota = set()
        for t in trajeto:
            u, v = t['origem'], t['destino']
            arestas_rota.append((u, v))
            nodos_rota.add(u)
            nodos_rota.add(v)
        
        nx.draw_networkx_nodes(G, pos, nodelist=list(nodos_rota), node_color='orange', node_size=2600)
        nx.draw_networkx_edges(G, pos, edgelist=arestas_rota, edge_color='red', width=3, arrowsize=25)
        
        labels_rota = { (u,v): edge_labels[(u,v)] for u,v in arestas_rota if (u,v) in edge_labels }
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels_rota, font_color='red', font_weight='bold')

    plt.title("Malha Aérea (Caminho Otimizado)" if trajeto else "Malha Aérea Completa")
    plt.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{data}"