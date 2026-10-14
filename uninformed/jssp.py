class JobShopData:
    """
    This class is used to store the data of a JSSP (Job-Shop
    Scheduling Problem) instance. The solvers communicate with
    objects of this class to generate solutions.
    """

    def __init__(self, filename, instance_name="unnamed"):
        self._name = instance_name
        self._jobs_data = []
        self._num_jobs = 0
        self._num_machines = 0
        self._horizon = 0 # Upper-bound for the solution
        self.load_from_file(filename)

    def load_from_file(self, filename):
        """
        This function loads the instance data from a txt file 
        according to the JSSP standard.
        """

        with open(filename, 'r') as f:
            lines = f.readlines()
            
        data_lines = []
        for line in lines:
            # Drop empty lines or lines with text (headers, or metadata)
            clean_line = line.strip()
            if not clean_line or clean_line.isalpha() or clean_line.startswith('-'):
                continue
            
            parts = clean_line.split()
            if any(p.isalpha() for p in parts):
                continue
                
            data_lines.append([int(x) for x in parts])
            
        # First line contains: (num_jobs, num_machines)
        self._num_jobs = data_lines[0][0]
        self._num_machines = data_lines[0][1]
        
        # The following lines contain: (machine, duration) pairs for each job
        for job_idx in range(1, self._num_jobs + 1):
            job_row = data_lines[job_idx]
            tasks = []
            for i in range(0, len(job_row), 2):
                machine = job_row[i]
                duration = job_row[i+1]
                tasks.append((machine, duration))
                self._horizon += duration
            self._jobs_data.append(tasks)

    def machine_count(self):
        return self._num_machines

    def job_count(self):
        return self._num_jobs

    def name(self):
        return self._name

    def horizon(self):
        return self._horizon

    def tasks_of_job(self, job_id):
        return self._jobs_data[job_id]

    def report(self):
        """
        This method prints the data of the instance.
        """
        print(f"Instance: {self._name}")
        print(f"Jobs: {self._num_jobs}, Machines: {self._num_machines}")
        print(f"Horizon (Makespan upper-bound): {self._horizon}")

    def report_all(self):
        self.report()
        for i, tasks in enumerate(self._jobs_data):
            print(f"Job {i}: {tasks}")