import random
import pandas as pd
from generator import generate_jssp_instance

if __name__ == "__main__":
    random.seed(31)  # Set a seed for reproducibility

    n_jobs_list = []
    n_machines_list = []

    # Classification parameters for instance generation
    # From (n_jobs, n_machines), up to (n_jobs, n_machines)
    classification = {
        "toy": [(3, 3), (5, 5)],
        "easy": [(6, 6), (10, 10)],
        "medium": [(11, 11), (15, 15)],
        "hard": [(16, 16), (20, 20)],
    }

    # How many instances to generate per classification
    n_instances = {
        "toy": 5,
        "easy": 20,
        "medium": 10,
        "hard": 5,
    }

    # Start generating instances...
    counter = 1
    for instance_type, ranges in classification.items():
        (min_jobs, min_machines), (max_jobs, max_machines) = ranges

        # Generate the specified number of instances...
        for _ in range(n_instances[instance_type]):
            num_jobs = random.randint(min_jobs, max_jobs)
            num_machines = random.randint(min_machines, max_machines)
            seed = random.randint(0, 100000)
            instance_name = f"jb{counter:02d}"
            filepath = f"instances/{instance_name}.txt"

            print(f"Generating instance {instance_name}...")
            generate_jssp_instance(
                num_jobs=num_jobs,
                num_machines=num_machines,
                min_duration=1,
                max_duration=99,
                seed=seed,
                instance_name=instance_name,
                filepath=filepath
            )

            # Update the lists for registry
            n_jobs_list.append(num_jobs)
            n_machines_list.append(num_machines)
            counter += 1

    # Update the registry with the new instances
    new_entries = pd.DataFrame({
        "instance": [f"jb{idx:02d}" for idx in range(1, counter)],
        "jobs": n_jobs_list,
        "machines": n_machines_list,
        "classification": [_ for sublist in [[key]*n_instances[key]  for key in n_instances.keys()] for _ in sublist],
        "source": ["generated"] * (counter - 1)
    })
    registry_path = "instances/registry.csv"
    registry = pd.read_csv(registry_path)
    registry = pd.concat([registry, new_entries])
    registry.to_csv(registry_path, index=False)