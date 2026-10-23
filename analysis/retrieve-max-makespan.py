import sys
from pathlib import Path
import pandas as pd

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

def main():
    from jssp.jssp import JobShopData

    instances_dir = repo_root / "instances"
    registry_path = instances_dir / "registry.csv"
    instance_files = sorted(instances_dir.glob("*.txt"))
    registry = pd.read_csv(registry_path)

    if "instance" not in registry.columns:
        raise ValueError(f"{registry_path} must contain an 'instance' column.")
    if registry["instance"].duplicated().any():
        duplicates = registry.loc[registry["instance"].duplicated(), "instance"].tolist()
        raise ValueError(f"{registry_path} contains duplicate instances: {duplicates}")

    horizons = {
        instance_file.stem: JobShopData(
            str(instance_file), instance_name=instance_file.stem
        ).horizon()
        for instance_file in instance_files
    }

    registered_instances = set(registry["instance"])
    unregistered_instances = sorted(set(horizons) - registered_instances)
    if unregistered_instances:
        raise ValueError(
            f"Instances are missing from {registry_path}: {unregistered_instances}"
        )

    if "horizon" not in registry.columns:
        registry["horizon"] = pd.NA
    matching_rows = registry["instance"].isin(horizons)
    registry.loc[matching_rows, "horizon"] = (
        registry.loc[matching_rows, "instance"].map(horizons)
    )
    registry.to_csv(registry_path, index=False)
    print(f"Saved horizons for {len(horizons)} instances to {registry_path}.")


if __name__ == "__main__":
    main()