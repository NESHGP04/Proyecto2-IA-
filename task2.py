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