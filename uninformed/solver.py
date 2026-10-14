import math
import time


class TimeoutException(Exception):
    """
    Personalized exception to cease the search when a timeout is reached.
    """
    pass


class JobShopDFS:
    def __init__(self, jssp_data, verbose=True):
        self.data = jssp_data
        self.num_jobs = self.data.job_count()
        self.num_machines = self.data.machine_count()

        # Initialize the best makespan with the trivial upper-bound
        self.best_makespan = self.data.horizon()
        self.best_schedule = None
        self.verbose = verbose

        # Time control
        self.start_time = 0
        self.time_limit = None
        

    def solve(self, time_limit=60):
        self.start_time = time.time()
        self.time_limit = time_limit # 60 sec by default

        next_op_index = [0] * self.num_jobs 
        machine_free_time = [0] * self.num_machines
        job_free_time = [0] * self.num_jobs

        # Try to run the DFS search, but catch the timeout exception if it occurs
        try:
            self._dfs(next_op_index, machine_free_time, job_free_time, [])
        except TimeoutException:
            print(f"\n[!] Time limit reached ({self.time_limit}s). Stopping search.")

        return self.best_makespan, self.best_schedule

    def _dfs(self, next_op, machine_free, job_free, current_schedule):
        # Check if it is still on time
        if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:
            raise TimeoutException()

        # Goal Check: Are all jobs fully scheduled?
        # That is, if all the operations for each job have been scheduled.
        if all(next_op[j] >= len(self.data.tasks_of_job(j)) for j in range(self.num_jobs)):
            makespan = max(job_free)
            # If this complete schedule is better than the best found so far, update the best known solution
            if makespan < self.best_makespan:
                self.best_makespan = makespan
                self.best_schedule = list(current_schedule)
                if self.verbose:
                    print(f"New best makespan found: {self.best_makespan}")
            return

        # Try scheduling any valid next operation...
        for j in range(self.num_jobs):
            op_idx = next_op[j]
            tasks = self.data.tasks_of_job(j)

            # If the job has remaining operations, attempt to schedule the next one
            if op_idx < len(tasks):
                machine, duration = tasks[op_idx]

                # Start time is constrained by the job's previous task and the machine's availability
                start_time = max(job_free[j], machine_free[machine])
                end_time = start_time + duration
                
                # If this partial schedule already exceeds the best known makespan, prune it
                if end_time >= self.best_makespan:
                    continue

                # Apply the action: schedule this operation.
                next_op[j] += 1
                prev_job_free = job_free[j]
                prev_machine_free = machine_free[machine]
                
                job_free[j] = end_time
                machine_free[machine] = end_time
                current_schedule.append((j, op_idx, machine, start_time, end_time))

                # Recursive depth exploration
                self._dfs(next_op, machine_free, job_free, current_schedule)

                # Backtrack (Undo action; revert to previous state)
                current_schedule.pop()
                job_free[j] = prev_job_free
                machine_free[machine] = prev_machine_free
                next_op[j] -= 1