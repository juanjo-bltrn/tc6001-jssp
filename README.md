# Solving Job‑Shop Scheduling via Uninformed Search, Heuristic Search, Local Search, and CSP

A Python project for solving the Job-Shop Scheduling Problem (JSSP) with multiple algorithmic approaches, including uninformed search, heuristic methods, local search, and mixed-integer linear programming (MILP). The repository is built for experimentation with benchmark instances from the classic JSSP family, including generated cases (`jb01`-`jb40`) and standard benchmark files such as `ft06`, `ft10`, `ft20`, `la01`-`la40`.

## Overview

Job-Shop Scheduling is the problem of assigning operations of multiple jobs to machines while satisfying precedence constraints and minimizing the makespan (total completion time). This project compares different solution strategies:

- Uninformed search
  - DFS
  - UCS
- Heuristic search
  - Weighted A*
  - Beam Search
- Local search
  - Simulated Annealing
- MILP formulation using PuLP

Each solver is implemented using a Python Class. The `run.py` file is designed to load a solver, load instances from the `instances/` folder, solve them, and write the corresponding schedules to `solutions/` with execution logs stored in `solutions/logs.csv`. 

## Repository Structure

```text
.
├── analysis/                  # Analysis notebooks, plots, and result processing
├── generator/                 # Instance generation utilities
├── instances/                # JSSP benchmark and generated instance files
│   ├── registry.csv          # Metadata for all stored instances
│   └── *.txt                 # Individual JSSP instance files
├── jssp/                     # Core JSSP data model and solver implementations
│   ├── heuristic/
│   ├── local/
│   ├── milp/
│   ├── uninformed/
│   └── jssp.py               # Data parser and instance representation
├── solutions/                # Output schedules and logs
│   ├── logs.csv
│   └── <algorithm>/          # Results per solver/algorithm
├── requirements.txt          # Python dependency list
├── run.py                    # Entry point for benchmarking all instances
└── README.md                 # Project documentation
```

## Features

- Supports standard JSSP instance input format
- Loads and solves a full registry of benchmark and generated instances
- Runs multiple algorithm families from one entry point
- Writes per-instance schedules and experiment logs
- Includes supportive analysis scripts and visualization tooling

## Requirements

- Python 3.10+ recommended
- pip
- A virtual environment is recommended

The project dependencies are declared in `requirements.txt`:

- numpy
- pandas
- PuLP
- matplotlib
- notebook

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/juanjo-bltrn/tc6001-jssp.git
cd tc6001-jssp
python -m venv .venv
```

### On Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### On macOS/Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

Run the default benchmark workflow from the project root:

```bash
python run.py
```

This executes the default solver configuration (`algorithm="local-sa"`) against all instance files in `instances/` and saves results under `solutions/`.

The script automatically updates `solutions/logs.csv` with execution metadata such as the instance name, runtime, seed, time limit, and solver output.

## Running with Custom Parameters

You can customize execution in Python. You can also call it with alternative algorithm names (supported by the implementation) in your local branch or experimental pipeline.

```python
from run import main

main(
    instances_path="instances",
    solutions_path="solutions",
    algorithm="milp",
    seed=31,
    tl=None
)
```

## Instance Format

Each instance file is a plain text file located in `instances/*.txt`.

The parser expects the following structure:

1. First line: `n_jobs n_machines`
2. Then one row per job, each row containing pairs of `machine duration` values in the order of job operations

Example:

```text
3 3
0 3 1 6 2 4
1 2 0 5 2 3
2 1 0 7 2 5
```

The parser ignores empty lines and non-numeric metadata, so many benchmark files can be read directly without preprocessing.

## Output Format

Solution schedules are written in text files inside `solutions/<algorithm>/`.

Each line represents one scheduled operation with the following fields:

```text
job_id task_index machine start_time end_time
```

Example:

```text
0 0 1 0 85
1 0 2 0 52
2 0 0 0 35
2 1 3 35 81
```

The final objective is the makespan, which is the maximum completion time across all jobs.

## Instance Generation

The project includes generation utilities to create custom JSSP datasets for different difficulty levels.

```bash
python generator/generate.py
```

This script creates random instances for toy, easy, medium, and hard classes and appends the metadata to `instances/registry.csv`.

## Important Directories

### `instances/`
Contains benchmark and generated problem data. Files are named in the standard JSSP format and are registered in `instances/registry.csv`.

### `jssp/`
Contains the core implementation, including the `JobShopData` parser and solver-specific modules.

### `solutions/`
Stores generated schedules and experiment logs. Each algorithm can write to its own subdirectory.

### `analysis/`
Contains notebooks and scripts for plotting results, evaluating benchmark quality, and reviewing optimization outcomes.

## Logs and Results

Every run appends logs to `solutions/logs.csv`. Typical information includes:

- Instance name
- Runtime
- Algorithm name
- Seed
- Time limit
- Solver-specific output metrics

## Common Usage Flow

1. Place or generate an instance in `instances/`
2. Load it using `JobShopData`
3. Instantiate a solver in `jssp/<method>/`
4. Run the solver
5. Save the schedule to `solutions/<algorithm>/`
6. Inspect `solutions/logs.csv` for performance metrics
7. Generate the visualization of the solution using `analysis/visualizer.py/`