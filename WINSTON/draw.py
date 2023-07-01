import networkx as nx
import matplotlib.pyplot as plt


def create_network(model):
    G = nx.DiGraph()

    rules = []
    for rule in model:
        if ';' in rule:
            rules.extend(rule.split(';'))
        else:
            rules.append(rule)

    for rule in rules:
        predicate, args = rule.split("(")
        args = args[:-1].split(",")

        for arg in args:
            G.add_node(arg)

        G.add_edge(args[1], args[0], label=predicate)

    return G


def draw_network(G):
    pos = nx.spring_layout(G, seed=64)
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}

    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, width=2.0)
    nx.draw_networkx_labels(G, pos, font_color='black', font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.axis('off')
    plt.show()

