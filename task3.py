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

