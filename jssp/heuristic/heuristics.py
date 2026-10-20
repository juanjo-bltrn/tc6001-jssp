# ==============================================================================
#                  Heuristic Functions for Heuristic Search
# ==============================================================================

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


def mwrm_heuristic(jssp_data, next_op, machine_free, job_free):
    """
    Función heurística 'Most Work Remaining on Machine' (MWRM) para JSSP.
    Calcula la carga total de trabajo pendiente para cada máquina considerando
    todas las operaciones aún no agendadas de todos los trabajos, sumada al tiempo
    de liberación actual de la máquina (machine_free[m]).
    """
    num_jobs = jssp_data.job_count()
    num_machines = jssp_data.machine_count()

    # Makespan parcial acumulado g(S)
    g_val = max(max(job_free), max(machine_free)) if (job_free and machine_free) else 0

    # Acumular la duración de todas las operaciones pendientes asignadas a cada máquina
    machine_work = [0] * num_machines
    for j in range(num_jobs):
        tasks = jssp_data.tasks_of_job(j)
        op_idx = next_op[j]
        for k in range(op_idx, len(tasks)):
            machine, duration = tasks[k]
            machine_work[machine] += duration

    # Determinar el tiempo mínimo estimado para que finalice la máquina más saturada
    max_machine_completion = 0
    for m in range(num_machines):
        total_machine_time = machine_free[m] + machine_work[m]
        if total_machine_time > max_machine_completion:
            max_machine_completion = total_machine_time

    # El costo restante h(S) es la diferencia entre el cuello de botella por máquina y g(S)
    h_val = max(0, max_machine_completion - g_val)
    return h_val