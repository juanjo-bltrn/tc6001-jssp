import random

def generate_jssp_instance(num_jobs, num_machines, min_duration=1, max_duration=99, seed=None, instance_name=None, filepath=None):
    """
    Generates a random Job-Shop Scheduling Problem (JSSP) instance.
    
    Parameters:
        num_jobs (int): Number of jobs.
        num_machines (int): Number of machines.
        min_duration (int): Minimum processing time for an operation (default 1).
        max_duration (int): Maximum processing time for an operation (default 99).
        seed (int, optional): Random seed for reproducibility.
        instance_name (str, optional): Name of the instance header, just to track things...
        filepath (str, optional): File path to save the instance. If None, prints to stdout.
    
    Returns:
        str: The formatted JSSP instance content.
    """
    if seed is not None:
        random.seed(seed)
        
    if instance_name is None:
        instance_name = f"gen_{num_jobs}x{num_machines}"

    lines = [
        "-"*30,
        f"Instance {instance_name}",
        f"Generated instance with seed {seed}",
        "-"*30,
        f"{num_jobs} {num_machines}"
    ]

    for _ in range(num_jobs):
        # Generate a random permutation of machines
        # (each machine used exactly once per job,
        # as it is a standard JSSP assumption)
        machines = list(range(num_machines))
        random.shuffle(machines)
        
        job_tasks = []
        for m in machines:
            duration = random.randint(min_duration, max_duration)
            job_tasks.append(f"{m} {duration}")
            
        lines.append("  ".join(job_tasks))

    content = "\n".join(lines) + "\n"

    # Save to file if a filepath is provided
    if filepath:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Instance successfully saved to {filepath}")

    return content