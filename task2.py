'''
TASK 2

- MAX (Defensa)
- MIN (Hacker)
- Cada turno captura un nodo vecino
- Cada nodo tiene un valor

'''

import random
import time
import networkx as nx

#configuración con profundidad de bñusqueda 4
SEED = 42
NUM_NODOS = 18
PROBABILIDAD_ARISTA = 0.20
D_MAX = 4

random.seed(SEED)

#función para generar grafo
def generar_grafo(n=NUM_NODOS, p=PROBABILIDAD_ARISTA, seed=SEED):
    G = nx.erdos_renyi_graph(n, p, seed=seed)

    while not nx.is_connected(G):
        comp = list(nx.connected_components(G))
        u = random.choice(list(comp[0]))
        v = random.choice(list(comp[1]))
        G.add_edge(u, v)

    mapeo = {i: f"S{i}" for i in range(n)}
    return nx.relabel_nodes(G, mapeo)