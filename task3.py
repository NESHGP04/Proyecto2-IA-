'''
TASK 3

- Probabilidad de éxito: 80%
- Probabilidad de fallo: 20%
- Comparación:
    Minimax vs Random
    Expectiminimax vs Random

'''

from task2 import *
import random
import time

PROB_EXITO = 0.8
PROB_FALLO = 0.2

#expectiminmax
def expectiminimax(estado, profundidad, contador):
    contador[0] += 1

    if es_terminal(estado, profundidad):
        return evaluar(estado), None

    if estado.turno == "MAX":
        mejor_valor = float("-inf")
        mejor_accion = None

        for a in acciones(estado):
            valor = nodo_azar(estado, a, profundidad, contador)

            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = a

        return mejor_valor, mejor_accion

    else:  # MIN
        mejor_valor = float("inf")
        mejor_accion = None

        for a in acciones(estado):
            valor = nodo_azar(estado, a, profundidad, contador)

            if valor < mejor_valor:
                mejor_valor = valor
                mejor_accion = a

        return mejor_valor, mejor_accion
    
#nodo de azar
def nodo_azar(estado, accion, profundidad, contador):
    # ── ÉXITO (80%)
    estado_exito = resultado(estado, accion)
    val_exito, _ = expectiminimax(estado_exito, profundidad + 1, contador)

    # ── FALLO (20%)
    estado_fallo = estado.copia()
    estado_fallo.turno = "MIN" if estado.turno == "MAX" else "MAX"
    val_fallo, _ = expectiminimax(estado_fallo, profundidad + 1, contador)

    # Valor esperado
    return PROB_EXITO * val_exito + PROB_FALLO * val_fallo

#agentes
def agente_random(estado):
    acc = acciones(estado)
    return random.choice(acc) if acc else None

def agente_minimax(estado):
    return minimax(estado, 0, [0])[1]

def agente_expecti(estado):
    return expectiminimax(estado, 0, [0])[1]

#simulación de la partida
def jugar_partida(estado, agente_max, agente_min, pasos=15):
    estado_actual = estado.copia()

    for _ in range(pasos):
        if estado_actual.turno == "MAX":
            accion = agente_max(estado_actual)
        else:
            accion = agente_min(estado_actual)

        if accion is None:
            break

        # ── PROBABILIDAD DE FALLO
        if random.random() < PROB_EXITO:
            estado_actual = resultado(estado_actual, accion)
        else:
            # pierde turno
            estado_actual.turno = "MIN" if estado_actual.turno == "MAX" else "MAX"

    return evaluar(estado_actual)

#función de los experimentos para correr con minmax y con expectiminmax
def experimento(estado, N=20):
    print("\nEjecutando experimentos...")

    resultados_mm = []
    resultados_exp = []

    # ── Minimax vs Random
    for _ in range(N):
        val = jugar_partida(estado, agente_minimax, agente_random)
        resultados_mm.append(val)

    # ── Expectiminimax vs Random
    for _ in range(N):
        val = jugar_partida(estado, agente_expecti, agente_random)
        resultados_exp.append(val)

    print("\n" + "="*50)
    print("RESULTADOS PROMEDIO")
    print("="*50)

    print("Minimax vs Random:", sum(resultados_mm)/N)
    print("Expectiminimax vs Random:", sum(resultados_exp)/N)

