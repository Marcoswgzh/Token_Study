"""Aggregate raw data from rq2 experiment into a single csv file"""

# Main writer: Anna Kálmánczhelyi
from pathlib import Path
import pandas as pd
import re

# input and output
RAW_DIR = Path("data/raw/expiration")
OUTPUT_FILE = Path("data/processed/rq2_aggregated_data.csv")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Code writer: Anna Kálmánczhelyi
def extract_metadata(filename):
    """Get metadata from the input file"""

    stem = Path(filename).stem

    metadata = {
        "experiment_name": stem,
        "alphabet_type": "hex",
        "token_length": None,
        "ttl_seconds": None,
    }

    length_match = re.search(r"len(\d+)", stem)
    if length_match:
        metadata["token_length"] = int(length_match.group(1))

    ttl_match = re.search(r"ttl(\d+)", stem)
    if ttl_match:
        metadata["ttl_seconds"] = int(ttl_match.group(1))

    return metadata

# Code writer: Anna Kálmánczhelyi
def main():
    csv_files = sorted(RAW_DIR.glob("*.csv"))

    # catch if there aren't any csv files
    if not csv_files:
        print("No CSV files found in {RAW_DIR}.")
        return

    dfs = []

    for file_path in csv_files:
        df = pd.read_csv(file_path)

        metadata = extract_metadata(file_path)
        df["experiment_name"] = metadata["experiment_name"]
        df["alphabet_type"] = metadata["alphabet_type"]
        df["token_length"] = metadata["token_length"]
        df["ttl_seconds"] = metadata["ttl_seconds"]
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"Rows: {len(combined)}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()