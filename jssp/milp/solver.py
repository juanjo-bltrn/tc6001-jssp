import pulp

class milpSolver:
    def __init__(self, jssp_data, verbose=False):
        self.data = jssp_data
        self.num_jobs = self.data.job_count()
        self.num_machines = self.data.machine_count()
        self.verbose = verbose

        self.best_makespan = None
        self.best_schedule = None

    def solve(self):
        # Initialize continuous minimization MILP problem
        prob = pulp.LpProblem("JobShopScheduling", pulp.LpMinimize)

        # Upper bound constant for Big-M formulation
        M = self.data.horizon()

        # Decision Variables: Start time for operation k of job j
        S = {}
        for j in range(self.num_jobs):
            tasks = self.data.tasks_of_job(j)
            for k in range(len(tasks)):
                S[(j, k)] = prob.add_variable(
                    f"S_{j}_{k}", lowBound=0, cat=pulp.LpContinuous
                )

        # Decision Variable: Makespan (Cmax)
        Cmax = prob.add_variable("Cmax", lowBound=0, cat=pulp.LpContinuous)

        # Objective Function
        prob += Cmax, "Minimize_Makespan"

        # 1. Precedence Constraints & Makespan Lower Bounds
        for j in range(self.num_jobs):
            tasks = self.data.tasks_of_job(j)
            for k in range(len(tasks)):
                _, duration = tasks[k]

                # Operation (j, k+1) cannot start until operation (j, k) finishes
                if k < len(tasks) - 1:
                    prob += (
                        S[(j, k + 1)] >= S[(j, k)] + duration,
                        f"Precedence_{j}_{k}",
                    )

                # Makespan must exceed completion time of every operation
                prob += Cmax >= S[(j, k)] + duration, f"Makespan_Bound_{j}_{k}"

        # Group tasks by assigned machine for disjunctive constraints
        machine_tasks = {m: [] for m in range(self.num_machines)}
        for j in range(self.num_jobs):
            tasks = self.data.tasks_of_job(j)
            for k, (m, duration) in enumerate(tasks):
                machine_tasks[m].append((j, k, duration))

        # 2. Disjunctive Machine Capacity Constraints (No overlapping tasks)
        for m, ops in machine_tasks.items():
            num_ops = len(ops)
            for i in range(num_ops):
                for j_idx in range(i + 1, num_ops):
                    j1, k1, p1 = ops[i]
                    j2, k2, p2 = ops[j_idx]

                    # Binary variable: 1 if (j1, k1) runs before (j2, k2), else 0
                    y_var = prob.add_variable(
                        f"y_m{m}_{j1}_{k1}_{j2}_{k2}", cat=pulp.LpBinary
                    )

                    # Either (j1, k1) finishes before (j2, k2) starts...
                    prob += (
                        S[(j2, k2)] >= S[(j1, k1)] + p1 - M * (1 - y_var),
                        f"NoOverlap1_m{m}_{j1}_{k1}_{j2}_{k2}",
                    )
                    # ...or (j2, k2) finishes before (j1, k1) starts
                    prob += (
                        S[(j1, k1)] >= S[(j2, k2)] + p2 - M * y_var,
                        f"NoOverlap2_m{m}_{j1}_{k1}_{j2}_{k2}",
                    )

        # Solve using default PuLP solver (CBC) with no time limit
        msg = 1 if self.verbose else 0
        solver = pulp.COIN_CMD(msg=msg)

        # Run solver...
        solve_stats = prob.solve(solver)

        # Check solution status...
        has_solution = solve_stats.has_solution
        if has_solution:
            self.best_makespan = int(round(Cmax.value()))

            # Parse to the common format so it can be used with run.py :p
            schedule = []
            for j in range(self.num_jobs):
                tasks = self.data.tasks_of_job(j)
                for k, (m, duration) in enumerate(tasks):
                    start_val = int(round(S[(j, k)].value()))
                    end_val = start_val + duration
                    schedule.append((j, k, m, start_val, end_val))

            # Sort schedule by start time
            schedule.sort(key=lambda x: (x[3], x[0], x[1]))
            self.best_schedule = schedule

        return {"makespan": self.best_makespan}, self.best_schedule