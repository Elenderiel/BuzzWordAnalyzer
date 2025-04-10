import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network


def get_normalized_color(cmap, minFreq:float, maxFreq:float, frequency:float) -> tuple:
    #converts the frequency values to a rgba color between blue and red
    normalizedFreq = (frequency - minFreq) / (maxFreq - minFreq)
    rgba = cmap(normalizedFreq)
    color  = f'rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, 0.7)'
    return color


def visualize_graph(nodes:dict, edges:dict, commonWords:list):
    try:
        #adds node data and edge weights to nx graph
        G = nx.Graph()
        G.add_nodes_from([(node, values) for node, values in nodes.items()])
        G.add_weighted_edges_from([(x, y, weight) for (x, y), weight in edges.items()])
        G.remove_nodes_from(commonWords)

        #precomputes the node positions for pyvis
        positions = nx.spring_layout(G, seed=1, iterations=100, threshold=0.7e-3, k=5/len(nodes)**0.5)
        nt = Network(height='100vh', width='100%', notebook=False, filter_menu=True, bgcolor='rgb(20, 20, 20)')

        minFreq = min((word['frequency'] for word in nodes.values()))
        maxFreq = max((word['frequency'] for word in nodes.values()))
        cmap = plt.colormaps['coolwarm']

        #adds node to pyvis at precomputed positions
        for node, (x, y) in positions.items():
            color = 'rgba(50, 50, 50, 0.7)'
            size = 5
            #dynamic size of node and lable based on word count. node color from colormap based on frequency value
            if node in nodes: 
                size = nodes[node]['count']**0.5
                color = get_normalized_color(cmap, minFreq, maxFreq, (nodes[node]['frequency']))
            font = {'size': size*2, 'vadjust': -8, 'color': 'rgba(200, 200, 200, 0.7)'}
            nt.add_node(node, x=x * 1500, y=y * 1500, size=size*3, color=color, title=node, font=font)
         
        nt.toggle_drag_nodes(False)
        nt.toggle_physics(False)
        nt.show('word_graph.html', notebook=False)
    except Exception as e:
        print(f'an error occured while trying to create word graph: {e}')