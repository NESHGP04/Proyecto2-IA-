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
import matplotlib.pyplot as plt

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

#función para definir si el estado es terminal
def es_terminal(estado, profundidad):
    todos = set(estado.grafo.nodes())
    ocupados = estado.max_nodes | estado.min_nodes
    return profundidad == D_MAX or ocupados == todos

#función para evaluar
def evaluar(estado):
    valor_max = sum(estado.valores[n] for n in estado.max_nodes)
    valor_min = sum(estado.valores[n] for n in estado.min_nodes)
    return valor_max - valor_min

#algoritmo minmax
def minimax(estado, profundidad, contador):
    contador[0] += 1

    if es_terminal(estado, profundidad):
        return evaluar(estado), None

    if estado.turno == "MAX":
        mejor_valor = float("-inf")
        mejor_accion = None

        for a in acciones(estado):
            val, _ = minimax(resultado(estado, a), profundidad + 1, contador)

            if val > mejor_valor:
                mejor_valor = val
                mejor_accion = a

        return mejor_valor, mejor_accion

    else:
        mejor_valor = float("inf")
        mejor_accion = None

        for a in acciones(estado):
            val, _ = minimax(resultado(estado, a), profundidad + 1, contador)

            if val < mejor_valor:
                mejor_valor = val
                mejor_accion = a

        return mejor_valor, mejor_accion

#algoritmo alpha-beta
def alphabeta(estado, profundidad, alpha, beta, contador):
    contador[0] += 1

    if es_terminal(estado, profundidad):
        return evaluar(estado), None

    if estado.turno == "MAX":
        mejor_accion = None

        for a in acciones(estado):
            val, _ = alphabeta(resultado(estado, a), profundidad + 1, alpha, beta, contador)

            if val > alpha:
                alpha = val
                mejor_accion = a

            if alpha >= beta:
                break

        return alpha, mejor_accion

    else:
        mejor_accion = None

        for a in acciones(estado):
            val, _ = alphabeta(resultado(estado, a), profundidad + 1, alpha, beta, contador)

            if val < beta:
                beta = val
                mejor_accion = a

            if beta <= alpha:
                break

        return beta, mejor_accion
    
#función para inicializar el juego
def inicializar_juego(G):
    valores = {n: random.randint(1, 10) for n in G.nodes()}

    nodos = list(G.nodes())
    max_start = nodos[0]
    min_start = nodos[1]

    estado = Estado(
        G,
        valores,
        max_nodes={max_start},
        min_nodes={min_start},
        turno="MAX"
    )

    return estado

#función para visualizar grafo
def visualizar_grafo_juego(G, estado):
    pos = nx.spring_layout(G, seed=42)

    colores = []
    for nodo in G.nodes():
        if nodo in estado.max_nodes:
            colores.append("#2ecc71")  # verde (Defensa)
        elif nodo in estado.min_nodes:
            colores.append("#e74c3c")  # rojo (Hacker)
        else:
            colores.append("#bdc3c7")  # gris (libre)

    etiquetas = {
        n: f"{n}\n({estado.valores[n]})"
        for n in G.nodes()
    }

    plt.figure(figsize=(10, 7))
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels=etiquetas,
        node_color=colores,
        node_size=800,
        font_size=8
    )

    plt.title("Estado del Juego (Verde=Defensa, Rojo=Hacker)")
    plt.show()

#main
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║   TASK 2 · Minimax vs Alpha-Beta            ║")
    print("╚══════════════════════════════════════════════╝")

    G = generar_grafo()

    print("\nGrafo:")
    print("Nodos:", G.number_of_nodes())
    print("Aristas:", G.number_of_edges())

    estado = inicializar_juego(G)

    visualizar_grafo_juego(G, estado)

    print("\nValores de nodos:")
    for n, v in estado.valores.items():
        print(f"{n}: {v}")

    #minmax
    contador_mm = [0]
    t0 = time.time()
    valor_mm, accion_mm = minimax(estado, 0, contador_mm)
    t_mm = time.time() - t0

    #alpha-beta
    contador_ab = [0]
    t0 = time.time()
    valor_ab, accion_ab = alphabeta(estado, 0, float("-inf"), float("inf"), contador_ab)
    t_ab = time.time() - t0

    #resultados
    print("\n" + "="*50)
    print("MINIMAX")
    print("="*50)
    print("Mejor acción:", accion_mm)
    print("Valor:", valor_mm)
    print("Nodos explorados:", contador_mm[0])
    print("Tiempo:", f"{t_mm:.6f}s")

    print("\n" + "="*50)
    print("ALPHA-BETA")
    print("="*50)
    print("Mejor acción:", accion_ab)
    print("Valor:", valor_ab)
    print("Nodos explorados:", contador_ab[0])
    print("Tiempo:", f"{t_ab:.6f}s")

    if contador_mm[0] > 0:
        reduccion = (1 - contador_ab[0] / contador_mm[0]) * 100
        print("\nReducción de nodos:", f"{reduccion:.2f}%")