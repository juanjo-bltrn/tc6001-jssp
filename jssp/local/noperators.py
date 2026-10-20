import random

# ==============================================================================
#                   Neighborhood operators for Local Search
# ==============================================================================

def swap_adjacent_operator(state):
    """
    Operador de Intercambio Adyacente:
    Intercambia dos posiciones contiguas con trabajos distintos en la secuencia.
    """
    neighbor = list(state)
    n = len(neighbor)
    valid_indices = [i for i in range(n - 1) if neighbor[i] != neighbor[i + 1]]

    if valid_indices:
        idx = random.choice(valid_indices)
        neighbor[idx], neighbor[idx + 1] = neighbor[idx + 1], neighbor[idx]
    return neighbor


def random_swap_operator(state):
    """
    Operador de Intercambio Arbitrario (Random Swap):
    Intercambia dos posiciones cualesquiera elegidas al azar en la secuencia.
    """
    neighbor = list(state)
    n = len(neighbor)
    i, j = random.sample(range(n), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor


def shift_reinsertion_operator(state):
    """
    Operador de Inserción (Shift / Re-insertion):
    Remueve un trabajo de una posición aleatoria y lo inserta en otra posición.
    """
    neighbor = list(state)
    n = len(neighbor)
    i, j = random.sample(range(n), 2)
    elem = neighbor.pop(i)
    neighbor.insert(j, elem)
    return neighbor


def two_opt_operator(state):
    """
    Operador 2-Opt (invertir una subsecuencia):
    Invierte el orden del segmento comprendido entre dos índices aleatorios. Importado del TSP.
    """
    neighbor = list(state)
    n = len(neighbor)
    i, j = sorted(random.sample(range(n), 2))
    neighbor[i : j + 1] = reversed(neighbor[i : j + 1])
    return neighbor
