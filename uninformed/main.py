from jssp import JobShopData
from solver import JobShopDFS
import time
 

def main():
    # 1. Load the instance data from the standard text file
    name = "jb05"
    filename = f"instances/{name}.txt"
    print(f"Loading instance from {filename}...")
    
    jssp_instance = JobShopData(filename, instance_name=name)
    
    # Report basic data
    jssp_instance.report()
    print("-" * 30)
    
    # 2. Initialize the DFS Solver with the parsed data
    solver = JobShopDFS(jssp_instance)
    
    # 3. Run the solver
    print("Starting DFS Search...")
    start = time.perf_counter() # Start measuring time
    makespan, schedule = solver.solve()
    
    # 4. Output results
    end = time.perf_counter()
    print("-" * 30)
    print(f"Execution time: {end - start} s") 
    print(f"Best makespan found: {makespan}")
    print("Schedule (Job, Op_Index, Machine, Start, End):")
    if schedule:
        for step in schedule:
            print(step)
    else:
        print("No valid schedule found.")

if __name__ == "__main__":
    main()