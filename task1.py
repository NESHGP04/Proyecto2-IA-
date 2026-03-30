'''
TASK 1: Configuración Segura de la Red (CSP y Factor Graphs)

Modelado como Factor Graph:
  - Variables   : X = {S0, S1, ..., Sn} — servidores de la red
  - Dominios    : D_i = {Rojo, Verde, Azul, Amarillo} para todo i
  - Factores    : f(Si, Sj) = [Si ≠ Sj]  (restricción binaria por cada arista)
  - Objetivo    : arg max_x Weight(x) = ∏ f_j(x)
                  Weight(x) = 1 iff todas las restricciones son satisfechas
'''

import random
import time
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ─────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────

SEED = 42
NUM_NODOS = 18          # entre 15 y 20
PROBABILIDAD_ARISTA = 0.20

PROTOCOLOS = ["Rojo", "Verde", "Azul", "Amarillo"]

COLORES_VIZ = {
    "Rojo":     "#e74c3c",
    "Verde":    "#2ecc71",
    "Azul":     "#3498db",
    "Amarillo": "#f1c40f",
    None:       "#bdc3c7"   # sin asignar
}

# ─────────────────────────────────────────────
# 1. GENERACIÓN DEL GRAFO
# ─────────────────────────────────────────────

def generar_grafo(n=NUM_NODOS, p=PROBABILIDAD_ARISTA, seed=SEED):
    """
    Genera un grafo aleatorio de n nodos con probabilidad p de arista.
    Se usa seed fija para reproducibilidad.
    Se garantiza que el grafo sea conexo (requisito de red operativa).
    """
    random.seed(seed)
    # Erdos-Renyi con seed fija
    G = nx.erdos_renyi_graph(n, p, seed=seed)

    # Garantizar conexidad: unir componentes con aristas aleatorias
    while not nx.is_connected(G):
        componentes = list(nx.connected_components(G))
        # Tomar un nodo de cada una de las primeras dos componentes y unirlos
        u = random.choice(list(componentes[0]))
        v = random.choice(list(componentes[1]))
        G.add_edge(u, v)

    # Renombrar nodos como "S0", "S1", etc.
    mapeo = {i: f"S{i}" for i in range(n)}
    G = nx.relabel_nodes(G, mapeo)
    return G


# ─────────────────────────────────────────────
# 2. FACTOR GRAPH — funciones de factor
# ─────────────────────────────────────────────

def factor(xi_val, xj_val):
    """
    Factor binario de restricción de diferencia.
    f(Xi, Xj) = [Xi ≠ Xj]
    Devuelve 1 si los protocolos son distintos, 0 si son iguales.
    Una asignación es consistente iff Weight(x) = ∏ f_j(x) = 1
    """
    return 1 if xi_val != xj_val else 0


def peso_asignacion_parcial(asignacion, grafo):
    """
    Calcula el peso de una asignación parcial.
    Solo evalúa los factores D(x, Xi) — aquellos cuyos dos extremos
    ya están asignados (slide: 'factores dependientes').
    Weight_parcial = ∏ f_j para todo factor completamente evaluable.
    """
    peso = 1
    for (u, v) in grafo.edges():
        if u in asignacion and v in asignacion:
            peso *= factor(asignacion[u], asignacion[v])
    return peso


# ─────────────────────────────────────────────
# 3. BACKTRACKING PURO
# ─────────────────────────────────────────────

def backtracking_puro(grafo):
    """
    Backtracking Search sin heurísticas ni lookahead.
    Basado directamente en el algoritmo:
      Backtrack(x, w, Domains):
        - Si x es asignación completa → actualizar mejor, regresar
        - Elegir variable Xi no asignada (orden fijo)
        - Para cada valor v en Domain_i:
            δ = ∏ f_j(x ∪ {Xi:v})   para fj en D(x, Xi)
            Si δ = 0 → continuar
            Backtrack(x ∪ {Xi:v}, w*δ, Domains)
    """
    nodos = list(grafo.nodes())
    asignacion = {}
    contador = [0]   # contador de asignaciones intentadas

    def backtrack(idx):
        # Caso base: asignación completa
        if idx == len(nodos):
            return dict(asignacion)

        nodo = nodos[idx]   # elegir variable (orden fijo, sin MRV)

        for protocolo in PROTOCOLOS:
            contador[0] += 1
            asignacion[nodo] = protocolo

            # δ = producto de factores dependientes ya evaluables
            # (slide: D(x, Xi) = factores que dependen de Xi y x pero
            #          no de variables no asignadas)
            delta = 1
            for vecino in grafo.neighbors(nodo):
                if vecino in asignacion:
                    delta *= factor(protocolo, asignacion[vecino])

            # Si δ = 0, esta asignación viola alguna restricción → skip
            if delta == 0:
                del asignacion[nodo]
                continue

            resultado = backtrack(idx + 1)
            if resultado is not None:
                return resultado

            del asignacion[nodo]

        return None   # backtrack

    inicio = time.time()
    solucion = backtrack(0)
    tiempo = time.time() - inicio

    return solucion, contador[0], tiempo


# ─────────────────────────────────────────────
# 4. BACKTRACKING OPTIMIZADO (MRV + FORWARD CHECKING)
# ─────────────────────────────────────────────

def seleccionar_variable_mrv(no_asignados, dominios):
    """
    Heurística MRV (Minimum Remaining Values) / Variable más restringida.
    'Elija la variable que tenga el dominio más pequeño.'
    Principio Fail-First: si va a fallar, falle temprano → más poda.
    """
    return min(no_asignados, key=lambda nodo: len(dominios[nodo]))


def forward_checking(nodo, valor, grafo, dominios):
    """
    Lookahead (Forward Checking):
    'Después de asignar Xi, elimine los valores inconsistentes
     de los dominios de los vecinos de Xi.'
    Devuelve los dominios actualizados y una lista de (vecino, valor_eliminado)
    para poder hacer rollback si es necesario.
    """
    eliminados = []
    for vecino in grafo.neighbors(nodo):
        if valor in dominios[vecino]:
            dominios[vecino].remove(valor)
            eliminados.append((vecino, valor))
    return eliminados


def restaurar_dominios(eliminados, dominios):
    """Revierte los cambios del forward checking al hacer backtrack."""
    for (vecino, valor) in eliminados:
        dominios[vecino].add(valor)


def backtracking_optimizado(grafo):
    """
    Backtracking Search con:
      - MRV: elegir la variable con menor dominio restante
      - Forward Checking (Lookahead): eliminar valores inconsistentes
        en vecinos después de cada asignación
    
    El algoritmo completo:
      Backtrack(x, w, Domains):
        Xi ← variable con menor |Domain_i|  (MRV)
        Para cada v en Domain_i:
          δ ← ∏ f_j(x ∪ {Xi:v}) para fj en D(x,Xi)
          Si δ = 0 → continuar
          Domains' ← Domains via LOOKAHEAD
          Si cualquier Domains'_i está vacío → continuar
          Backtrack(x ∪ {Xi:v}, w*δ, Domains')
    """
    nodos = list(grafo.nodes())
    asignacion = {}
    # Cada nodo empieza con su dominio completo (conjunto mutable)
    dominios = {nodo: set(PROTOCOLOS) for nodo in nodos}
    contador = [0]

    def backtrack(no_asignados):
        # Caso base: asignación completa
        if not no_asignados:
            return dict(asignacion)

        # MRV: elegir variable con menor dominio restante
        nodo = seleccionar_variable_mrv(no_asignados, dominios)
        no_asignados_restantes = no_asignados - {nodo}

        for protocolo in list(dominios[nodo]):
            contador[0] += 1
            asignacion[nodo] = protocolo

            # δ = producto de factores dependientes (slide: D(x, Xi))
            delta = 1
            for vecino in grafo.neighbors(nodo):
                if vecino in asignacion:
                    delta *= factor(protocolo, asignacion[vecino])

            if delta == 0:
                del asignacion[nodo]
                continue

            # LOOKAHEAD: Forward Checking
            # Eliminar el protocolo asignado de dominios de vecinos no asignados
            eliminados = forward_checking(nodo, protocolo, grafo, dominios)

            # Si algún dominio quedó vacío → fallo, continuar
            dominio_vacio = any(
                len(dominios[v]) == 0
                for v in grafo.neighbors(nodo)
                if v not in asignacion
            )

            if not dominio_vacio:
                resultado = backtrack(no_asignados_restantes)
                if resultado is not None:
                    return resultado

            # Rollback: restaurar dominios eliminados
            restaurar_dominios(eliminados, dominios)
            del asignacion[nodo]

        return None   # backtrack

    inicio = time.time()
    solucion = backtrack(set(nodos))
    tiempo = time.time() - inicio

    return solucion, contador[0], tiempo


# ─────────────────────────────────────────────
# 5. VERIFICACIÓN DE SOLUCIÓN
# ─────────────────────────────────────────────

def verificar_solucion(solucion, grafo):
    """
    Verifica que Weight(x) = 1, es decir, que todas las restricciones
    f(Si, Sj) = [Si ≠ Sj] sean satisfechas.
    """
    if solucion is None:
        return False
    for (u, v) in grafo.edges():
        if factor(solucion[u], solucion[v]) == 0:
            return False
    return True


# ─────────────────────────────────────────────
# 6. VISUALIZACIÓN
# ─────────────────────────────────────────────

def visualizar_grafo(grafo, solucion, titulo="Red de Servidores"):
    """
    Visualiza el grafo con los protocolos asignados como colores.
    """
    pos = nx.spring_layout(grafo, seed=SEED)

    colores_nodos = [
        COLORES_VIZ.get(solucion.get(nodo), COLORES_VIZ[None])
        for nodo in grafo.nodes()
    ]

    plt.figure(figsize=(12, 8))
    nx.draw_networkx(
        grafo,
        pos=pos,
        node_color=colores_nodos,
        node_size=800,
        font_size=8,
        font_weight="bold",
        edge_color="#7f8c8d",
        width=1.5,
        with_labels=True
    )

    # Leyenda de protocolos
    leyenda = [
        mpatches.Patch(color=COLORES_VIZ[p], label=p)
        for p in PROTOCOLOS
    ]
    plt.legend(handles=leyenda, loc="upper left", title="Protocolo")
    plt.title(titulo)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("red_servidores.png", dpi=150)
    plt.show()
    print("Gráfico guardado como 'red_servidores.png'")


# ─────────────────────────────────────────────
# 7. ANÁLISIS COMPARATIVO
# ─────────────────────────────────────────────

def imprimir_resultados(nombre, solucion, conteo, tiempo, grafo):
    print(f"\n{'='*55}")
    print(f"  {nombre}")
    print(f"{'='*55}")
    valido = verificar_solucion(solucion, grafo)
    print(f"  Solución válida    : {'✓ SÍ' if valido else '✗ NO'}")
    print(f"  Asignaciones int.  : {conteo}")
    print(f"  Tiempo de ejecución: {tiempo:.6f} segundos")
    if solucion:
        print(f"\n  Asignación de protocolos:")
        for nodo, protocolo in sorted(solucion.items()):
            print(f"    {nodo:4s} → {protocolo}")


# ─────────────────────────────────────────────
# 8. MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║  CC3045 · Proyecto 2 · Task 1: CSP y Factor Graphs   ║")
    print("╚══════════════════════════════════════════════════════╝")

    # Generar grafo
    G = generar_grafo()
    print(f"\nGrafo generado:")
    print(f"  Nodos   : {G.number_of_nodes()}")
    print(f"  Aristas : {G.number_of_edges()}")
    print(f"  Conexo  : {nx.is_connected(G)}")
    print(f"  Seed    : {SEED}")

    # ── Backtracking PURO ──────────────────────────────
    print("\n[1/2] Ejecutando Backtracking puro...")
    sol_puro, conteo_puro, tiempo_puro = backtracking_puro(G)
    imprimir_resultados("BACKTRACKING PURO", sol_puro, conteo_puro, tiempo_puro, G)

    # ── Backtracking OPTIMIZADO (MRV + FC) ────────────
    print("\n[2/2] Ejecutando Backtracking optimizado (MRV + Forward Checking)...")
    sol_opt, conteo_opt, tiempo_opt = backtracking_optimizado(G)
    imprimir_resultados("BACKTRACKING + MRV + FORWARD CHECKING", sol_opt, conteo_opt, tiempo_opt, G)

    # ── COMPARACIÓN ───────────────────────────────────
    print(f"\n{'='*55}")
    print(f"  ANÁLISIS COMPARATIVO")
    print(f"{'='*55}")
    if conteo_puro > 0:
        reduccion_conteo = (1 - conteo_opt / conteo_puro) * 100
        reduccion_tiempo = (1 - tiempo_opt / tiempo_puro) * 100
        print(f"  Asignaciones puro       : {conteo_puro}")
        print(f"  Asignaciones optimizado : {conteo_opt}")
        print(f"  Reducción de intentos   : {reduccion_conteo:.1f}%")
        print(f"  Tiempo puro             : {tiempo_puro:.6f}s")
        print(f"  Tiempo optimizado       : {tiempo_opt:.6f}s")
        print(f"  Speedup                 : {tiempo_puro/tiempo_opt:.2f}x más rápido")

    # ── VISUALIZACIÓN ─────────────────────────────────
    if sol_opt:
        visualizar_grafo(G, sol_opt, titulo="Red de Servidores — Protocolo Asignado (MRV + FC)")