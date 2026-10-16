import heapq
import time


class TimeoutException(Exception):
    """
    Personalized exception to cease the search when a timeout is reached.
    """
    pass


def combined_bound_heuristic(jssp_data, next_op, machine_free, job_free):
    """
    Función heurística admisible basada en la combinación de cotas inferiores 
    por Trabajo (Job Bound) y por Máquina (Machine Bound).
    
    Retorna la estimación h(S) del tiempo adicional mínimo necesario para
    completar todas las operaciones pendientes desde el estado actual.
    """
    num_jobs = jssp_data.job_count()
    num_machines = jssp_data.machine_count()

    # Makespan parcial actual g(S)
    g_val = max(max(job_free), max(machine_free)) if (job_free and machine_free) else 0

    # 1. Job Lower Bound
    # Para cada trabajo, calcula su tiempo de finalización mínimo ignorando las máquinas
    max_job_completion = 0
    for j in range(num_jobs):
        tasks = jssp_data.tasks_of_job(j)
        rem_duration = sum(tasks[k][1] for k in range(next_op[j], len(tasks)))
        max_job_completion = max(max_job_completion, job_free[j] + rem_duration)

    # 2. Machine Lower Bound
    # Para cada máquina, acumula el tiempo de procesamiento de sus operaciones pendientes
    machine_work = [0] * num_machines
    for j in range(num_jobs):
        tasks = jssp_data.tasks_of_job(j)
        for k in range(next_op[j], len(tasks)):
            machine, duration = tasks[k]
            machine_work[machine] += duration

    max_machine_completion = 0
    for m in range(num_machines):
        max_machine_completion = max(max_machine_completion, machine_free[m] + machine_work[m])

    # Preserve the max of both bounds as the estimated makespan
    total_estimated_makespan = max(max_job_completion, max_machine_completion)

    # h(S) representa el costo restante relativo a g(S)
    h_val = max(0, total_estimated_makespan - g_val)
    return h_val





class JobShopWeightedAStar:
    """
    A Weighted A* Search with pruning for the Job Shop Scheduling Problem (JSSP).
    
    Uses two parameters:
    - weight (w): Peso aplicado a la heurística f(S) = g(S) + w * h(S).
    - heuristic_fn: Función heurística a utilizar.
    """
    def __init__(self, jssp_data, weight=1.0, heuristic_fn=combined_bound_heuristic, verbose=True):
        self.data = jssp_data
        self.num_jobs = self.data.job_count()
        self.num_machines = self.data.machine_count()
        self.weight = weight
        self.heuristic_fn = heuristic_fn

        # Initialize the best makespan with the trivial upper-bound
        self.best_makespan = self.data.horizon()
        self.best_schedule = None
        self.verbose = verbose

        # Time control
        self.start_time = 0
        self.time_limit = None

        self.exp_nodes = 0  # Counter for expanded nodes

    def solve(self, time_limit=None):
        self.start_time = time.time()
        self.time_limit = time_limit

        # Try to run the Weighted A* search, but catch the timeout exception if it occurs
        try:
            self._a_star()
        except TimeoutException:
            print(f"\n[!] Time limit reached ({self.time_limit}s). Stopping search.")

        print(f"Total expanded nodes: {self.exp_nodes}")
        return {"makespan": self.best_makespan, "expanded_nodes": self.exp_nodes, "weight": self.weight, "heuristic": self.heuristic_fn.__name__}, self.best_schedule

    def _a_star(self):
        # Priority Queue stores tuples:
        # (f_val, g_val, counter_tie_breaker, next_op, machine_free, job_free, current_schedule)
        counter = 0  # Tie-breaker counter to ensure unique ordering in the priority queue
        pq = []

        initial_next_op = [0] * self.num_jobs
        initial_machine_free = [0] * self.num_machines
        initial_job_free = [0] * self.num_jobs
        initial_schedule = []

        # Estado inicial
        initial_g = 0
        initial_h = self.heuristic_fn(self.data, initial_next_op, initial_machine_free, initial_job_free)
        initial_f = initial_g + self.weight * initial_h

        heapq.heappush(
            pq,
            (initial_f, initial_g, counter, initial_next_op, initial_machine_free, initial_job_free, initial_schedule, ),
        )

        while pq:
            # Control de límite de tiempo
            if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:
                raise TimeoutException()

            self.exp_nodes += 1  # Update the count of expanded nodes

            # Saca el nodo con el menor f(S) de la cola de prioridad
            f_val, g_val, _, next_op, machine_free, job_free, current_schedule = heapq.heappop(pq)

            # Pruning: Si el costo g del nodo actual ya alcanza o supera la mejor solución global, se descarta
            if g_val >= self.best_makespan:
                continue

            # Goal Check: Are all jobs fully scheduled?
            if all(next_op[j] >= len(self.data.tasks_of_job(j)) for j in range(self.num_jobs)):
                if g_val < self.best_makespan:
                    self.best_makespan = g_val
                    self.best_schedule = current_schedule
                    if self.verbose:
                        print(f"New best makespan found: {self.best_makespan}")
                continue

            # Expansion of successors
            for j in range(self.num_jobs):
                op_idx = next_op[j]
                tasks = self.data.tasks_of_job(j)

                if op_idx < len(tasks):
                    machine, duration = tasks[op_idx]

                    start_time = max(job_free[j], machine_free[machine])
                    end_time = start_time + duration

                    # Pruning: If the end time of this operation already exceeds the best known makespan, skip it
                    if end_time >= self.best_makespan:
                        continue

                    # Copy state structures for child node
                    new_next_op = list(next_op)
                    new_next_op[j] += 1

                    new_machine_free = list(machine_free)
                    new_machine_free[machine] = end_time

                    new_job_free = list(job_free)
                    new_job_free[j] = end_time

                    new_schedule = list(current_schedule)
                    new_schedule.append((j, op_idx, machine, start_time, end_time))

                    # Cost calculations
                    new_g = max(new_job_free)
                    new_h = self.heuristic_fn(
                        self.data, new_next_op, new_machine_free, new_job_free
                    )
                    new_f = new_g + self.weight * new_h

                    counter += 1
                    heapq.heappush(
                        pq,
                        (
                            new_f,
                            new_g,
                            counter,
                            new_next_op,
                            new_machine_free,
                            new_job_free,
                            new_schedule,
                        ),
                    )


class JobShopBeamSearch:
    """
    A Beam Search solver with pruning for the Job Shop Scheduling Problem (JSSP).
    Beam Search explora por niveles y conserva únicamente los K mejores estados
    (beam_width) en cada paso de expansión.
    
    Parámetros:
    - beam_width (K): Ancho del haz (número máximo de estados retribuidos por nivel).
    - heuristic_fn: Función heurística para evaluar los estados f(S) = g(S) + h(S).
    """

    def __init__(
        self,
        jssp_data,
        beam_width=5,
        heuristic_fn=combined_bound_heuristic,
        verbose=True,
    ):
        self.data = jssp_data
        self.num_jobs = self.data.job_count()
        self.num_machines = self.data.machine_count()
        self.beam_width = beam_width
        self.heuristic_fn = heuristic_fn

        # Initialize the best makespan with the trivial upper-bound
        self.best_makespan = self.data.horizon()
        self.best_schedule = None
        self.verbose = verbose

        # Time control
        self.start_time = 0
        self.time_limit = None

        self.exp_nodes = 0  # Counter for expanded nodes

    def solve(self, time_limit=None):
        self.start_time = time.time()
        self.time_limit = time_limit

        # Try to run Beam Search, catch the timeout exception if it occurs
        try:
            self._beam_search()
        except TimeoutException:
            print(f"\n[!] Time limit reached ({self.time_limit}s). Stopping search.")

        print(f"Total expanded nodes: {self.exp_nodes}")
        return {
            "makespan": self.best_makespan,
            "expanded_nodes": self.exp_nodes,
            "beam_width": self.beam_width,
            "heuristic": self.heuristic_fn.__name__
        }, self.best_schedule

    def _beam_search(self):
        initial_next_op = [0] * self.num_jobs
        initial_machine_free = [0] * self.num_machines
        initial_job_free = [0] * self.num_jobs
        initial_schedule = []

        initial_g = 0
        initial_h = self.heuristic_fn(
            self.data, initial_next_op, initial_machine_free, initial_job_free
        )
        initial_f = initial_g + initial_h

        # Nivel actual (beam): Lista de estados de la forma (f_val, g_val, next_op, machine_free, job_free, schedule)
        current_beam = [
            (
                initial_f,
                initial_g,
                initial_next_op,
                initial_machine_free,
                initial_job_free,
                initial_schedule,
            )
        ]

        while current_beam:
            # Control de límite de tiempo global por nivel
            if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:
                raise TimeoutException()

            next_candidates = []

            # Expande todos los nodos conservados en el nivel/haz actual
            for f_val, g_val, next_op, machine_free, job_free, current_schedule in current_beam:
                if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:
                    raise TimeoutException()

                self.exp_nodes += 1

                # Pruning por mejor makespan global conocido
                if g_val >= self.best_makespan:
                    continue

                # Goal Check: ¿Todas las tareas de todos los trabajos están agendadas?
                if all(next_op[j] >= len(self.data.tasks_of_job(j)) for j in range(self.num_jobs)):
                    if g_val < self.best_makespan:
                        self.best_makespan = g_val
                        self.best_schedule = current_schedule
                        if self.verbose:
                            print(f"New best makespan found: {self.best_makespan}")
                    continue

                # Generación de sucesores
                for j in range(self.num_jobs):
                    op_idx = next_op[j]
                    tasks = self.data.tasks_of_job(j)

                    if op_idx < len(tasks):
                        machine, duration = tasks[op_idx]

                        start_time = max(job_free[j], machine_free[machine])
                        end_time = start_time + duration

                        # Pruning temprano
                        if end_time >= self.best_makespan:
                            continue

                        new_next_op = list(next_op)
                        new_next_op[j] += 1

                        new_machine_free = list(machine_free)
                        new_machine_free[machine] = end_time

                        new_job_free = list(job_free)
                        new_job_free[j] = end_time

                        new_schedule = list(current_schedule)
                        new_schedule.append((j, op_idx, machine, start_time, end_time))

                        new_g = max(new_job_free)
                        new_h = self.heuristic_fn(
                            self.data, new_next_op, new_machine_free, new_job_free
                        )
                        new_f = new_g + new_h

                        next_candidates.append(
                            (
                                new_f,
                                new_g,
                                new_next_op,
                                new_machine_free,
                                new_job_free,
                                new_schedule,
                            )
                        )

            if not next_candidates:
                break

            # Ordena los candidatos del nivel por f_val ascendente (y desempata por mayor g_val)
            next_candidates.sort(key=lambda item: (item[0], -item[1]))

            # Aplica el ancho de haz K: conserva solo los K mejores estados
            current_beam = next_candidates[: self.beam_width]