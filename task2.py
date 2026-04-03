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

#clase estado, con funciones para inciarlo y devolverlo
class Estado:
    def __init__(self, grafo, valores, max_nodes=None, min_nodes=None, turno="MAX"):
        self.grafo = grafo
        self.valores = valores
        self.max_nodes = set(max_nodes or [])
        self.min_nodes = set(min_nodes or [])
        self.turno = turno

    def copia(self):
        return Estado(
            self.grafo,
            self.valores,
            self.max_nodes.copy(),
            self.min_nodes.copy(),
            self.turno
        )
    
#función para realizar acciones
def acciones(estado):
    if estado.turno == "MAX":
        controlados = estado.max_nodes
    else:
        controlados = estado.min_nodes

    posibles = set()

    for nodo in controlados:
        for vecino in estado.grafo.neighbors(nodo):
            if vecino not in estado.max_nodes and vecino not in estado.min_nodes:
                posibles.add(vecino)

    return list(posibles)

#función para realizar transiciones
def resultado(estado, accion):
    nuevo = estado.copia()

    if estado.turno == "MAX":
        nuevo.max_nodes.add(accion)
        nuevo.turno = "MIN"
    else:
        nuevo.min_nodes.add(accion)
        nuevo.turno = "MAX"

    return nuevo