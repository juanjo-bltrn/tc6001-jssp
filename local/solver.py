import math
import random
import time

from operators import (
    swap_adjacent_operator,
    random_swap_operator,
    shift_reinsertion_operator,
    two_opt_operator
)

class TimeoutException(Exception):
    """
    Excepción personalizada para detener la búsqueda cuando se alcanza el límite de tiempo.
    """
    pass

# ==============================================================================
#          Decode permutation to valid schedule and compute makespan
# ==============================================================================

def decode_permutation(jssp_data, permutation):
    """
    Convierte un vector de representación por permutación (lista de IDs de trabajos)
    en un schedule válido y calcula su makespan (C_max).
    """
    num_jobs = jssp_data.job_count()
    num_machines = jssp_data.machine_count()

    next_op = [0] * num_jobs
    machine_free = [0] * num_machines
    job_free = [0] * num_jobs
    schedule = []

    for job_id in permutation:
        op_idx = next_op[job_id]
        tasks = jssp_data.tasks_of_job(job_id)
        machine, duration = tasks[op_idx]

        start_time = max(job_free[job_id], machine_free[machine])
        end_time = start_time + duration

        job_free[job_id] = end_time
        machine_free[machine] = end_time
        next_op[job_id] += 1

        schedule.append((job_id, op_idx, machine, start_time, end_time))

    makespan = max(job_free)
    return makespan, schedule


# ==============================================================================
# CLASE PRINCIPAL: SIMULATED ANNEALING SOLVER
# ==============================================================================


class SimulatedAnnealing:
    """
    Solver de Búsqueda Local con Simulated Annealing para el JSSP.

    Parámetros:
    -----------
    - jssp_data: Objeto JobShopData con la instancia del problema.
    - initial_temp: Temperatura inicial T_0 (por defecto 1000.0).
    - cooling_rate: Tasa de enfriamiento alpha en T_{k+1} = alpha * T_k (por defecto 0.995).
    - min_temp: Temperatura mínima / criterio de parada térmico (por defecto 1e-3).
    - max_iterations: Número máximo de iteraciones permitidas (por defecto 50000).
    - neighborhood_op: Función del operador de vecindario a utilizar.
    - verbose: Muestra información en consola sobre el avance del solver.
    """

    def __init__(self, jssp_data, initial_temp=1000.0, cooling_rate=0.995, min_temp=1e-3, max_iterations=50000, 
                 neighborhood_op=shift_reinsertion_operator, seed=31, verbose=True, 
                 ):
        self.data = jssp_data
        self.num_jobs = self.data.job_count()
        self.num_machines = self.data.machine_count()

        # Hiperparámetros de Recocido Simulado
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations
        self.neighborhood_op = neighborhood_op
        self.verbose = verbose

        # Estado global y mejor solución
        self.best_makespan = float("inf")
        self.best_schedule = None
        self.best_state = None

        # Control de tiempo y métricas de desempeño
        self.start_time = 0
        self.time_limit = None
        self.iterations_count = 0

        # Reproducibilidad
        self.seed = seed
        random.seed(self.seed)

    def _generate_initial_state(self):
        """
        Genera una solución inicial aleatoria en representación de permutación.
        """
        initial_perm = []
        for j in range(self.num_jobs):
            initial_perm.extend([j] * len(self.data.tasks_of_job(j)))
        random.shuffle(initial_perm)
        return initial_perm

    def solve(self, time_limit=None):
        """
        Ejecuta la búsqueda local por Simulated Annealing.
        """
        self.start_time = time.time()
        self.time_limit = time_limit

        try:
            self._simulated_annealing()
        except TimeoutException:
            if self.verbose:
                print(f"\n[!] Time limit reached ({self.time_limit}s). Stopping search.")


        if self.verbose:
            print(f"Iteraciones totales: {self.iterations_count}")

        return {
            "makespan": self.best_makespan,
            "iterations": self.iterations_count,
            "neighborhood": self.neighborhood_op.__name__,
            "initial_temp": self.initial_temp,
            "cooling_rate": self.cooling_rate,
            "min_temp": self.min_temp,
            "seed": self.seed
        }, self.best_schedule

    def _simulated_annealing(self):
        # 1. Generación de la Solución Inicial
        current_state = self._generate_initial_state()
        current_makespan, current_schedule = decode_permutation(
            self.data, current_state
        )

        # Inicialización de la mejor solución global
        self.best_makespan = current_makespan
        self.best_schedule = current_schedule
        self.best_state = list(current_state)

        if self.verbose:
            print(f"Makespan inicial: {current_makespan}")

        current_temp = self.initial_temp
        self.iterations_count = 0

        # 2. Bucle Principal de Recocido
        while (
            current_temp > self.min_temp
            and self.iterations_count < self.max_iterations
        ):
            # Verificación del límite de tiempo
            if (self.time_limit is not None and (time.time() - self.start_time) > self.time_limit):
                raise TimeoutException()

            self.iterations_count += 1

            # Generar solución vecina usando el operador seleccionado
            candidate_state = self.neighborhood_op(current_state)
            candidate_makespan, candidate_schedule = decode_permutation(self.data, candidate_state)

            # Variación en la función objetivo:
            delta = candidate_makespan - current_makespan

            # Criterio de aceptación...
            if delta < 0:
                accept = True
            else:
                prob = math.exp(-delta / current_temp)
                accept = random.random() < prob

            if accept:
                current_state = candidate_state
                current_makespan = candidate_makespan
                current_schedule = candidate_schedule

                # Actualizar óptimo global si mejora
                if current_makespan < self.best_makespan:
                    self.best_makespan = current_makespan
                    self.best_schedule = current_schedule
                    self.best_state = list(current_state)
                    if self.verbose:
                        print(
                            f"New best makespan found: {self.best_makespan} | Temp: {current_temp:.2f} | Iter: {self.iterations_count}"
                        )

            # Esquema de enfriamiento geométrico
            current_temp *= self.cooling_rate