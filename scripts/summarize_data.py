""" Summarize data from experiment trial csv """
# show: 
# - number of trials
# - success rate for each token length per ttl
# - avg success rate for each token length
# - avg success rate for each ttl 

# Main writer: Anna Kálmánczhelyi
from pathlib import Path
import pandas as pd

# Input and output configurations
AGGREGATED_FILE = Path("data/processed/rq2_aggregated_data.csv")
SUMMARY_OUTPUT_FILE = Path("data/processed/rq2_experiment_summary.csv")
TOKEN_AVG_OUTPUT_FILE = Path("data/processed/rq2_avg_by_token_length.csv")
TTL_AVG_OUTPUT_FILE = Path("data/processed/rq2_avg_by_ttl.csv")

def main():
    if not AGGREGATED_FILE.exists():
        print(f"Error: Aggregated file not found at {AGGREGATED_FILE}.")
        return

    print(f"Reading aggregated data from {AGGREGATED_FILE}")
    df = pd.read_csv(AGGREGATED_FILE)
    
    # Force data types to be boolean for accurate calculations
    df['success'] = df['success'].astype(bool)

    # Make sure output directory exists
    SUMMARY_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Number of trials and success rate for each token length per ttl
    summary_grain = df.groupby(['token_length', 'ttl_seconds']).agg(
        total_trials=('trial', 'count'),
        successful_trials=('success', 'sum'),
    ).reset_index()
    
    # Calculate success rate
    summary_grain['success_rate'] = summary_grain['successful_trials'] / summary_grain['total_trials']

    # Reorder columns and save primary summary
    column_order = ['token_length', 'ttl_seconds', 'total_trials', 'successful_trials', 'success_rate']
    summary_final = summary_grain[column_order]
    summary_final.to_csv(SUMMARY_OUTPUT_FILE, index=False)
    print(f"Saved granular summary to: {SUMMARY_OUTPUT_FILE}")


    # 2nd file: Avg success rate for each token length across all TTLs
    avg_per_token = summary_final.groupby('token_length')['success_rate'].mean().reset_index()
    
    # Rename column for clarification
    avg_per_token.columns = ['token_length', 'avg_success_rate']
    avg_per_token.to_csv(TOKEN_AVG_OUTPUT_FILE, index=False)
    print(f"Saved token length averages to: {TOKEN_AVG_OUTPUT_FILE}")


    # 3rd file: Avg success rate for each ttl across all token lenghts
    avg_per_ttl = summary_final.groupby('ttl_seconds')['success_rate'].mean().reset_index()
    
    #rename column for clarification
    avg_per_ttl.columns = ['ttl_seconds', 'avg_success_rate']
    avg_per_ttl.to_csv(TTL_AVG_OUTPUT_FILE, index=False)
    print(f"Saved TTL averages to: {TTL_AVG_OUTPUT_FILE}")


if __name__ == "__main__":
    main()