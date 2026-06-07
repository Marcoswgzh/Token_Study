""" Generate visualization plots from summarized experiment data """

# Main writer: Anna Kálmánczhelyi
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# Input and output paths
SUMMARY_FILE = Path("data/processed/rq2_experiment_summary.csv")
TOKEN_AVG_FILE = Path("data/processed/rq2_avg_by_token_length.csv")
TTL_AVG_FILE = Path("data/processed/rq2_avg_by_ttl.csv")
PLOT_DIR = Path("plots")

def main():
    # check if the 3 files exist from summarize_data.py (they're needed for the plot genreation)
    if not (SUMMARY_FILE.exists() and TOKEN_AVG_FILE.exists() and TTL_AVG_FILE.exists()):
        print("Error: Summary CSV files not found.")
        return

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    
    sns.set_theme(style="whitegrid", context="talk")

    # Load data and ensure proper sorting for line drawing
    df_summary = pd.read_csv(SUMMARY_FILE)
    df_summary = df_summary.sort_values(by=['token_length', 'ttl_seconds'])

    
    # Plot 1: continuous graph like on the poster
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot a line + marker combo for each unique token length
    sns.lineplot(
        data=df_summary,
        x='ttl_seconds',
        y='success_rate',
        hue='token_length',
        style='token_length',  
        markers=True,
        markersize=10,
        linewidth=2.5,
        palette='Set1',
        ax=ax
    )
    
    # Formatting 
    ax.set_title('Success Rate Over Expiration Windows (TTL)', fontsize=16, pad=15, weight='bold')
    ax.set_xlabel('TTL Window (seconds)', fontsize=13, labelpad=10)
    ax.set_ylabel('Success Rate (%)', fontsize=13, labelpad=10)
    ax.set_ylim(-0.05, 1.05)  
    
    # Set X-axis tick locations to ttl second locations (or whatever)
    unique_ttls = sorted(df_summary['ttl_seconds'].unique())
    ax.set_xticks(unique_ttls)
    
    # Convert Y-axis decimals to percentages 
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    
    # Legend configuration (outside the box, for clarity)
    ax.legend(
        title="Token Length", 
        bbox_to_anchor=(1.05, 1),
        loc='upper left',  
        frameon=True, 
        shadow=True
    )
    plt.tight_layout()
    line_plot_path = PLOT_DIR / "rq2_success_rate_trends.png"
    plt.savefig(line_plot_path, dpi=300)
    plt.close()


    # Plot 2: Average Success Rate by Token Length
    df_token = pd.read_csv(TOKEN_AVG_FILE).sort_values(by='token_length')
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_token, x='token_length', y='avg_success_rate', hue='token_length', palette='viridis', ax=ax)
    ax.set_title('Average Success Rate by Token Length', fontsize=15, pad=15)
    ax.set_xlabel('Token Length', fontsize=12)
    ax.set_ylabel('Average Success Rate', fontsize=12)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    
    # same as for prev plot
    ax.legend(
        title="Token Length", 
        bbox_to_anchor=(1.05, 1),  
        loc='upper left', 
        frameon=True, 
        shadow=True
    )

    plt.tight_layout()
    plt.savefig(PLOT_DIR / "rq2_avg_success_by_token_length.png", dpi=300)
    plt.close()

    # Plot 3: Average Success Rate by TTL Window
    df_ttl = pd.read_csv(TTL_AVG_FILE).sort_values(by='ttl_seconds')
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_ttl, x='ttl_seconds', y='avg_success_rate', hue='ttl_seconds', palette='magma', ax=ax)
    ax.set_title('Average Success Rate by TTL Window', fontsize=15, pad=15)
    ax.set_xlabel('TTL (seconds)', fontsize=12)
    ax.set_ylabel('Average Success Rate', fontsize=12)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    
    #same as before
    ax.legend(
        title="Token Length", 
        bbox_to_anchor=(1.05, 1), 
        loc='upper left', 
        frameon=True, 
        shadow=True
    )

    plt.tight_layout()
    plt.savefig(PLOT_DIR / "rq2_avg_success_by_ttl.png", dpi=300)
    plt.close()

    # Plot 4: Heatmap of Success Rates
    if len(df_summary['token_length'].unique()) > 1 or len(df_summary['ttl_seconds'].unique()) > 1:
        pivot_df = df_summary.pivot(index='token_length', columns='ttl_seconds', values='success_rate')
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            pivot_df, 
            annot=True, 
            fmt=".1%", 
            cmap="YlGnBu", 
            vmin=0, 
            vmax=1, 
            ax=ax,
            cbar_kws={'label': 'Success Rate (%)'},
            annot_kws={"size": 11}
        )
        ax.set_title('Success Rate Matrix by Token Length & TTL', fontsize=14, pad=15, weight='bold')
        ax.set_xlabel('TTL (seconds)', fontsize=12, labelpad=10)
        ax.set_ylabel('Token Length', fontsize=12, labelpad=10)
        
        plt.savefig(PLOT_DIR / "rq2_success_rate_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()
    else:
        print("Skipping Heatmap bc more than 1 experimental configuration's needed")

    print(f"\nAll plots generated successfully. Check them in the '{PLOT_DIR}/' folder.")


if __name__ == "__main__":
    main()