import os
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from graph_query import get_info_by_node, get_album_by_node
from curved_edges import curved_edges

root_dir = os.path.join(os.path.dirname(__file__), os.pardir)
filepath = os.path.join(root_dir, 'data', 'graph', 'graph_connections.csv')

#filtro de peso para melhorar visualizacao
graph_connections = pd.read_csv(filepath)
mean = graph_connections['Weight'].mean()
print('Weight mean: ', mean)
graph_connections_filtered = graph_connections[graph_connections['Weight'] > mean]
graph_connections_filtered.to_csv(os.path.join(root_dir, 'data', 'graph', 'graph_connections_filtered.csv'), index=False)
vis_filepath = os.path.join(root_dir, 'data', 'graph', 'graph_connections_filtered.csv')

data = open(filepath, "r")
next(data, None)
Graphtype = nx.Graph()
G = nx.parse_edgelist(data, delimiter=',', create_using=Graphtype, nodetype=int, data=(('weight', float), ('reverse_weight', float)))
data.close()

print(G)

def to_vector(tuple_list):
    sorted_list = sorted(tuple_list.items())
    return [item for _, item in sorted_list]

def get_similar(node):
    distance = nx.single_source_dijkstra_path_length(G, node, weight='reverse_weight')
    sorted_distance = sorted(distance, key=distance.get)
    album_list = [get_album_by_node(node) for node in sorted_distance]
    return album_list

def calculate_metrics():
    degree_centrality = G.degree(weight='weight')
    average_path_length = nx.average_shortest_path_length(G, weight='reverse_weight') # also add without weight
    average_path_length_unweighted = nx.average_shortest_path_length(G)
    closeness_centrality = nx.closeness_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G, weight='reverse_weight')
    communities = nx.community.louvain_communities(G, weight='weight', resolution=3, seed=72)
    triangles = nx.triangles(G)
    clustering = nx.clustering(G, weight='weight')
    average_clustering = nx.average_clustering(G, weight='weight')

    
    filename = os.path.join(root_dir, 'data', 'graph', 'general_metrics.txt')
    with open(filename, 'w', encoding='utf-8') as f:
        print(f"Average path length: {average_path_length}", end='\n\n', file=f)
        print(f"Unweighted average path length: {average_path_length_unweighted}", end='\n\n', file=f)
        print(f"Average clustering: {average_clustering}", end='\n\n', file=f)

    node_to_community = dict()
    for index, community in enumerate(communities):
        for vertex in community:
            node_to_community[vertex] = index

    data_dict = {'node': [i for i in range(1,1001)]}

    sorted_degrees = sorted(degree_centrality)
    data_dict['degree'] = [degree for _, degree in sorted_degrees]

    data_dict['closeness'] = to_vector(closeness_centrality)
    data_dict['betweenness'] = to_vector(betweenness_centrality)
    data_dict['community'] = to_vector(node_to_community)
    data_dict['triangles'] = to_vector(triangles)
    data_dict['clustering'] = to_vector(clustering)

    df = pd.DataFrame(data_dict).set_index('node')
    df.to_csv(os.path.join(root_dir, 'data', 'graph', 'vertex_metrics.csv'))

def main():

    album_similarities = []
    for i in range(1,2):
        album_similarities.append(get_similar(i))
    (pd.DataFrame(album_similarities)).to_csv(os.path.join(root_dir, 'data', 'graph', 'album_similarities.csv'))
    
    # calculate_metrics()
    communities = nx.community.louvain_communities(G, weight='weight', resolution=3, seed=72)
    communities_filename = os.path.join(root_dir, '.\data\graph\general_metrics.txt')

    node_to_community = dict()
    node_colors = []


    with open(communities_filename, 'w', encoding='utf-8') as f:
        # adicionar informações sobre as comunidades ao arquivo
        modularity = nx.community.modularity(G, communities, weight='weight')
        print(f"Communities: Modularity = {modularity}", file=f)
        for index, community in enumerate(communities):
            print(index, file=f)
            print(community, file=f)
            print(get_info_by_node(community, ['genre', 'second_genre', 'artist','descriptor']), end='\n\n', file=f)

            # colore os vértices com base na comunidade
            for vertex in community: # col
                node_to_community[vertex] = index
                node_colors.append(index)

    vis_data = open(vis_filepath, "r")
    next(vis_data, None)
    G_vis = nx.parse_edgelist(vis_data, delimiter=',', create_using=Graphtype, nodetype=int, data=(('weight', float), ('reverse_weight', float)))
    vis_data.close()
'''
    pos = nx.spring_layout(G_vis, weight='weight', seed=69, k=0.33, iterations=20)
    curves = curved_edges(G_vis, pos, dist_ratio=0.1, bezier_precision=20, polarity='random')
    
    weights = np.array([x[2]['weight'] for x in G.edges(data=True)])
    widths = 0.7 * np.log(weights)
    lc = LineCollection(curves, color='k', alpha=0.05, linewidths=widths)

    plt.figure(figsize=(20,20))
    plt.gca().add_collection(lc)
    plt.tick_params(axis='both',which='both',bottom=False,left=False,labelbottom=False,labelleft=False)
    nx.draw_networkx_nodes(G, pos, node_size=25, node_color=node_colors)
    plt.show()
'''
    # nx.draw_networkx_nodes(G_vis, pos=pos, node_size=4, node_color=node_colors)
    # nx.draw_networkx_edges(G_vis, pos=pos, alpha=0.02, node_size=4, connectionstyle="arc3,rad=0.70")
    # plt.show()

if __name__ == "__main__":
    main()