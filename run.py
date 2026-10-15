"""
This file is used to run an experiment: 
An algorithm tries to solve all the JSSP instances in the 'instances' folder, 
and the results are saved in the 'solutions' folder.
Also, all the results are saved in the logs file in the 'solutions' folder.
"""

# Import the necessary modules to run the experiment
from uninformed.jssp import JobShopData as Jssp
from uninformed.solver import JobShopDFS as Solver
from datetime import datetime
import time
import pandas as pd
import os

def main(instances_path = "instances", solutions_path = "solutions", algorithm="uninformed-dfs", seed=None, tl=60):
    # Lists to store the log information for each instance
    timestamps = []
    makespans = []
    runtimes = []
    expanded_nodes_list = []
    instances = [f.split('.')[0] for f in os.listdir(instances_path) if os.path.isfile(os.path.join(instances_path, f)) and f.endswith('.txt')]
    # instances = instances[:10]  # Limit to the first 10 instances for testing purposes

    print(f"[i] {len(instances)} instances found. Running {algorithm}...")
    

    for name in instances:
        # 1. Load the instance data from the standard text file
        filename = f"{instances_path}/{name}.txt"
        outpath = f"{solutions_path}/{algorithm}/{name}.txt"
        print(f"Loading instance from {filename}...")

        # Inicializar la instancia JSSP
        jssp_instance = Jssp(filename, instance_name=name)
        
        # Report basic data about the instance
        jssp_instance.report()
        print("-" * 30)
        
        # 2. Initialize the solver with the parsed data
        solver = Solver(jssp_instance)
        
        # 3. Run the solver...
        print("Excecuting solver...")
        now = datetime.now()
        start = time.perf_counter() # Start measuring time
        results, schedule = solver.solve(time_limit=tl)

        # Extract the results
        makespan = results["makespan"]
        expanded_nodes = results["expanded_nodes"]
        
        # 4. Output results
        end = time.perf_counter()
        print("-" * 30)
        print(f"Execution time: {end - start} s") 
        print(f"Best makespan found: {makespan}")

        # Check if a valid schedule was found...
        if schedule:
            content = ""
            for step in schedule:
                step_str = f"{step[0]} {step[1]} {step[2]} {step[3]} {step[4]}"
                content += step_str + "\n"
            # Save to file if a filepath is provided
            if outpath:
                with open(outpath, "w") as f:
                    f.write(content)
                print(f"Instance successfully saved to {outpath}")
        else:
            print("[!] No valid schedule found.")

        # Record the log information for this instance
        timestamps.append(now.strftime("%Y-%m-%d %H:%M:%S"))
        makespans.append(makespan)
        runtimes.append(end - start)
        expanded_nodes_list.append(expanded_nodes)

    # Save the logs to a CSV file
    new_logs = pd.DataFrame({
        "timestamp": timestamps,
        "algorithm": [algorithm] * len(instances),
        "instance": instances,
        "time_limit": [tl] * len(instances),
        "seed": [seed] * len(instances),
        "makespan": makespans,
        "runtime": runtimes,
        "expanded_nodes": expanded_nodes_list
    })
    logs_path = "solutions/logs.csv"
    logs = pd.read_csv(logs_path)
    logs = pd.concat([logs, new_logs])
    logs.to_csv(logs_path, index=False)

    print(f"[i] Experiment completed. Results saved in {solutions_path}/{algorithm}/ and logs updated in {solutions_path}/logs.csv.")

if __name__ == "__main__":
    main()