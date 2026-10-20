import csv
import json
from collections import defaultdict
from pathlib import Path

working_directory = Path.cwd()
repo_root = next(
    (
        path
        for path in (working_directory, *working_directory.parents)
        if (path / "instances").is_dir() and (path / "solutions").is_dir()
    ),
    None,
)
if repo_root is None:
    raise FileNotFoundError("Could not locate the repository root from the notebook's working directory.")

instance_names = {
    path.stem
    for path in (repo_root / "instances").glob("*.txt")
    if path.stem.startswith(("ft", "la"))
}
benchmark_path = repo_root / "solutions" / "benchmark-solutions"
optimal_candidates = defaultdict(list)

for results_path in sorted(benchmark_path.glob("results_*.json")):
    with results_path.open(encoding="utf-8") as results_file:
        results = json.load(results_file)

    for result in results:
        instance = result["instance"]
        if instance not in instance_names:
            continue

        lower_bound = result["lb"]["value"]
        upper_bound = result["ub"]["value"]
        if lower_bound == upper_bound:
            solver = result["ub"].get("solver") or results_path.stem[len("results_"):]
            optimal_candidates[instance].append((lower_bound, solver.lower()))

conflicting_optima = {
    instance: sorted({makespan for makespan, _ in candidates})
    for instance, candidates in optimal_candidates.items()
    if len({makespan for makespan, _ in candidates}) > 1
}
if conflicting_optima:
    raise ValueError(f"Conflicting proven optima found across benchmark files: {conflicting_optima}")

optimal_results = {
    instance: candidates[0]
    for instance, candidates in optimal_candidates.items()
}

optimals_path = repo_root / "solutions" / "optimals.csv"
with optimals_path.open(newline="", encoding="utf-8") as optimals_file:
    reader = csv.DictReader(optimals_file)
    fieldnames = reader.fieldnames
    if fieldnames is None:
        raise ValueError(f"{optimals_path} has no CSV header.")

    columns = {field.strip(): field for field in fieldnames}
    required_columns = {"instance", "makespan", "solver"}
    if not required_columns.issubset(columns):
        raise ValueError(f"{optimals_path} must contain columns: {sorted(required_columns)}")

    rows = list(reader)

rows_by_instance = {row[columns["instance"]]: row for row in rows}
missing_rows = optimal_results.keys() - rows_by_instance.keys()
if missing_rows:
    raise ValueError(f"Instances are missing from {optimals_path}: {sorted(missing_rows)}")

for instance, (makespan, solver) in optimal_results.items():
    row = rows_by_instance[instance]
    row[columns["makespan"]] = str(makespan)
    row[columns["solver"]] = solver

with optimals_path.open("w", newline="", encoding="utf-8") as optimals_file:
    writer = csv.DictWriter(optimals_file, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(optimal_results)} proven ft/la optima from benchmark result files to {optimals_path}.")