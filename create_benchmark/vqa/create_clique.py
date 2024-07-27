import matplotlib.pyplot as plt
import networkx as nx
import random

# Define the clique members
clique_members = [
    "174", "209", "286", "701", "1239", "1299", "2828",
    "2914", "3257", "3320", "3356", "3491", "5511",
    "6453", "6461", "6762", "6830", "7018", "12956"
]

def generate_clique_image(members):
    # Create a graph
    G = nx.Graph()

    # Add nodes
    G.add_nodes_from(members)

    # Add edges to form a clique
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            G.add_edge(members[i], members[j])

    # Define positions of the nodes
    pos = {
        members[0]: (0, 1),
        members[1]: (1, 1),
        members[2]: (0, 0),
        members[3]: (1, 0)
    }

    # Draw the nodes
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='white', edgecolors='black')

    # Draw the edges
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), style='dashed')

    # Draw the labels
    nx.draw_networkx_labels(G, pos, labels={node: f"{node}:transit degree" for node in members}, font_size=10)

    # Add clique labels
    plt.text(-0.3, 0.5, 'clique', fontsize=12, ha='center')
    plt.text(1.3, 0.5, 'clique', fontsize=12, ha='center')

    # Display the plot
    plt.title('Clique Graph Example')
    plt.axis('off')
    plt.show()

def select_and_generate_clique(clique_members, n=4):
    selected_members = random.sample(clique_members, n)
    generate_clique_image(selected_members)

# Example usage:
select_and_generate_clique(clique_members)